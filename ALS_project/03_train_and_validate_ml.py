"""
Step 3: Supervised 20-Gene Biomarker Classifier & Hold-Out Validation Prototype
- Zero data leakage: 80/20 stratified split BEFORE feature selection and scaling.
- Evaluates 5-fold CV + unseen 20% hold-out test set (Accuracy, ROC-AUC, Confusion Matrix).
- Saves trained model (.pkl) and runs a live prediction demo on unseen test patients.
"""

import os
import gzip
import pickle
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    classification_report,
)

OUT_DIR = "als_ideathon_outputs"
GZ_PATH = "GSE234297_gene_raw_counts.txt.gz"
LABELS_CSV = os.path.join(OUT_DIR, "sals_subtype_assignments.csv")

SUBTYPE_META = {
    "ALS-Subtype-1": {
        "name": "ALS-SG / Interferon-Stress",
        "pathway": "Stress Granule Assembly & Type-I Interferon",
        "drugs": "Withaferin A (Adj. p=5.82e-8), Celastrol (Adj. p=6.19e-4)",
    },
    "ALS-Subtype-2": {
        "name": "ALS-Ox / Vascular-Immune",
        "pathway": "H2O2 Catabolic Process & Complement Activation",
        "drugs": "PHA-767491 (exploratory), Docetaxel (exploratory)",
    },
}


def map_entrez_to_symbol(entrez_ids: list) -> dict:
    try:
        resp = requests.post(
            "https://mygene.info/v3/gene",
            data={"ids": ",".join(map(str, entrez_ids)), "fields": "symbol"},
            timeout=20,
        )
        resp.raise_for_status()
        return {
            str(item.get("query", "")): item.get("symbol", str(item.get("query", "")))
            for item in resp.json()
        }
    except Exception:
        return {str(i): str(i) for i in entrez_ids}


def load_sals_matrix():
    with gzip.open(GZ_PATH, "rt") as f:
        df = pd.read_csv(f, sep=None, engine="python", index_col=0)

    labels_df = pd.read_csv(LABELS_CSV)
    samples = labels_df["Sample"].tolist()
    df = df[samples].apply(pd.to_numeric, errors="coerce").fillna(0)

    # Filter lowly expressed genes & normalize (CPM + log2)
    keep_mask = (df >= 10).sum(axis=1) >= int(0.20 * df.shape[1])
    df_filt = df.loc[keep_mask]
    cpm = df_filt.div(df_filt.sum(axis=0), axis=1) * 1e6
    log_cpm = np.log2(cpm + 1.0)

    X = log_cpm.T  # samples x genes
    X.columns = X.columns.astype(str)
    y = (labels_df["Subtype"] == "ALS-Subtype-1").astype(int).values  # 1 = Subtype-1, 0 = Subtype-2
    return X, y, labels_df


def main():
    X, y, labels_df = load_sals_matrix()
    print(f"[INFO] Loaded {X.shape[0]} sALS patients x {X.shape[1]} genes")

    # 1. Strict 80/20 Stratified Split BEFORE any feature selection
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, labels_df["Sample"].values, test_size=0.20, stratify=y, random_state=42
    )
    print(f"[INFO] Train set: {len(X_train)} patients | Unseen Hold-Out Test set: {len(X_test)} patients")

    # 2. Supervised Pipeline: Select Top 20 Genes (on Train only) -> Scale -> Logistic Regression
    pipe = Pipeline(
        [
            ("select", SelectKBest(score_func=f_classif, k=20)),
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(C=1.0, max_iter=1000, random_state=42)),
        ]
    )

    # 5-Fold Cross-Validation on Training Set
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_auc = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="roc_auc")
    cv_acc = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="accuracy")
    print(f"\n[CV] 5-Fold Train ROC-AUC:  {cv_auc.mean():.3f} +/- {cv_auc.std():.3f}")
    print(f"[CV] 5-Fold Train Accuracy: {cv_acc.mean():.3f} +/- {cv_acc.std():.3f}")

    # 3. Fit on full Training Set & Evaluate on Unseen Hold-Out Test Set
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]

    test_acc = accuracy_score(y_test, y_pred)
    test_auc = roc_auc_score(y_test, y_prob)
    print(f"\n[TEST] Unseen Hold-Out Accuracy: {test_acc:.3f}")
    print(f"[TEST] Unseen Hold-Out ROC-AUC:  {test_auc:.3f}")
    print("\n[TEST] Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["ALS-Ox (Subtype-2)", "ALS-SG (Subtype-1)"]))

    # 4. Extract Top 20 Selected Biomarker Genes
    mask = pipe.named_steps["select"].get_support()
    selected_ids = X.columns[mask].tolist()
    coefs = pipe.named_steps["clf"].coef_[0]
    sym_map = map_entrez_to_symbol(selected_ids)

    panel_df = pd.DataFrame(
        {
            "Entrez_ID": selected_ids,
            "Gene_Symbol": [sym_map.get(i, i) for i in selected_ids],
            "Model_Weight": coefs,
            "Direction": ["Higher in ALS-SG" if w > 0 else "Higher in ALS-Ox" for w in coefs],
        }
    ).sort_values("Model_Weight", key=abs, ascending=False)
    panel_df.to_csv(os.path.join(OUT_DIR, "top20_biomarker_panel.csv"), index=False)
    print("[INFO] Top 10 genes in the 20-gene blood diagnostic panel:")
    print(panel_df.head(10).to_string(index=False))

    # 5. Save Trained Model Artifact (.pkl)
    model_path = os.path.join(OUT_DIR, "als_subtype_classifier.pkl")
    with open(model_path, "wb") as f:
        pickle.dump({"pipeline": pipe, "gene_columns": X.columns.tolist()}, f)
    print(f"\n[SAVED] Trained classifier saved to {model_path}")

    # 6. Plot ROC Curve + Confusion Matrix
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), dpi=150)
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    axes[0].plot(fpr, tpr, color="#3186ff", lw=2.2, label=f"Hold-Out ROC (AUC = {test_auc:.3f})")
    axes[0].plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5)
    axes[0].set_xlabel("False Positive Rate")
    axes[0].set_ylabel("True Positive Rate")
    axes[0].set_title("20-Gene Classifier ROC (Unseen 20% Test Set)")
    axes[0].legend(loc="lower right")

    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        xticklabels=["ALS-Ox", "ALS-SG"],
        yticklabels=["ALS-Ox", "ALS-SG"],
        ax=axes[1],
    )
    axes[1].set_xlabel("Predicted Subtype")
    axes[1].set_ylabel("True Subtype")
    axes[1].set_title(f"Hold-Out Confusion Matrix (Acc = {test_acc:.1%})")

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "ml_validation_roc_cm.png"))
    plt.close()

    # 7. Live Unseen-Patient Prototype Demo
    print("\n=== LIVE UNSEEN-PATIENT PROTOTYPE DEMO ===")
    for i in range(min(3, len(X_test))):
        sample_id = idx_test[i]
        prob_sg = y_prob[i]
        pred_key = "ALS-Subtype-1" if prob_sg >= 0.5 else "ALS-Subtype-2"
        conf = prob_sg if prob_sg >= 0.5 else (1.0 - prob_sg)
        meta = SUBTYPE_META[pred_key]
        print(
            f"Patient: {sample_id}\n"
            f"  -> Predicted Subtype: {meta['name']} ({conf:.1%} confidence)\n"
            f"  -> Core Pathway:      {meta['pathway']}\n"
            f"  -> Matched Drugs:     {meta['drugs']}"
        )


if __name__ == "__main__":
    main()