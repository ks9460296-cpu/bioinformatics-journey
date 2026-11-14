"""
Step 4: Interactive Live Patient Prototype (Supports Brand-New Walk-In CSVs)
- Loads the trained 20-gene ML model (als_subtype_classifier.pkl).
- Auto-generates a template 20-gene CSV (als_ideathon_outputs/new_walkin_patient.csv)
  that you can edit or replace with any external patient's 20-gene panel values.
- Supports both external walk-in CSVs ('csv') and GSE234297 test samples ('Case19', 'random').
"""

import os
import gzip
import pickle
import random
import numpy as np
import pandas as pd

OUT_DIR = "als_ideathon_outputs"
MODEL_PATH = os.path.join(OUT_DIR, "als_subtype_classifier.pkl")
PANEL_CSV = os.path.join(OUT_DIR, "top20_biomarker_panel.csv")
DEFAULT_WALKIN_CSV = os.path.join(OUT_DIR, "new_walkin_patient.csv")
GZ_PATH = "GSE234297_gene_raw_counts.txt.gz"

SUBTYPE_INFO = {
    1: {
        "name": "ALS-SG / Interferon-Stress (Subtype 1)",
        "pathway": "Stress Granule Assembly (C9ORF72, TIA1, DDX3X) & Type-I Interferon",
        "drugs": "Withaferin A (Adj. p=5.82e-8), Celastrol (Adj. p=6.19e-4)",
    },
    0: {
        "name": "ALS-Ox / Vascular-Immune (Subtype 2)",
        "pathway": "H2O2 Catabolic Process (HBM, HBA1, HBQ1) & Complement Activation",
        "drugs": "PHA-767491 (exploratory, Adj. p=0.108), Docetaxel (exploratory)",
    },
}


def load_prototype():
    with open(MODEL_PATH, "rb") as f:
        saved = pickle.load(f)
    pipe = saved["pipeline"]
    gene_cols = saved["gene_columns"]

    with gzip.open(GZ_PATH, "rt") as f:
        df = pd.read_csv(f, sep=None, engine="python", index_col=0)

    case_cols = [c for c in df.columns if "case" in c.lower() or "als" in c.lower()]
    df = df[case_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    df.index = df.index.astype(str)

    cpm = df.div(df.sum(axis=0), axis=1) * 1e6
    log_cpm = np.log2(cpm + 1.0)
    X_all = log_cpm.reindex(gene_cols, fill_value=0).T
    return pipe, gene_cols, X_all


def ensure_walkin_template(X_all: pd.DataFrame):
    """Create a sample external walk-in patient 20-gene CSV if it doesn't exist."""
    if os.path.exists(DEFAULT_WALKIN_CSV) or not os.path.exists(PANEL_CSV):
        return
    panel_df = pd.read_csv(PANEL_CSV)
    panel_df["Entrez_ID"] = panel_df["Entrez_ID"].astype(str)
    # Pre-fill with cohort median log2(CPM+1) values as a realistic starting template
    medians = X_all[panel_df["Entrez_ID"].tolist()].median()
    template = pd.DataFrame(
        {
            "Gene_Symbol": panel_df["Gene_Symbol"],
            "Entrez_ID": panel_df["Entrez_ID"],
            "Log2_CPM_Expression": [round(float(medians[eid]), 3) for eid in panel_df["Entrez_ID"]],
        }
    )
    template.to_csv(DEFAULT_WALKIN_CSV, index=False)
    print(f"[INFO] Created walk-in patient template CSV: {DEFAULT_WALKIN_CSV}")


def print_prediction(patient_label: str, pipe, row_df: pd.DataFrame):
    pred_class = int(pipe.predict(row_df)[0])
    prob_sg = float(pipe.predict_proba(row_df)[0, 1])
    confidence = prob_sg if pred_class == 1 else (1.0 - prob_sg)

    info = SUBTYPE_INFO[pred_class]
    print("\n" + "=" * 64)
    print(f"  PATIENT ID:        {patient_label}")
    print(f"  PREDICTED SUBTYPE: {info['name']}")
    print(f"  MODEL CONFIDENCE:  {confidence:.1%}")
    print(f"  CORE PATHWAY:      {info['pathway']}")
    print(f"  MATCHED DRUGS:     {info['drugs']}")
    print("=" * 64)


def predict_from_csv(csv_path: str, pipe, gene_cols: list):
    if not os.path.exists(csv_path):
        print(f"  [!] File not found: {csv_path}")
        return
    df_in = pd.read_csv(csv_path)
    if "Log2_CPM_Expression" not in df_in.columns:
        print("  [!] CSV must have a 'Log2_CPM_Expression' column (plus 'Entrez_ID' or 'Gene_Symbol').")
        return

    # Map Gene_Symbol -> Entrez_ID using top20_biomarker_panel.csv if Entrez_ID is missing
    if "Entrez_ID" not in df_in.columns and os.path.exists(PANEL_CSV):
        panel_df = pd.read_csv(PANEL_CSV)
        sym_to_entrez = dict(zip(panel_df["Gene_Symbol"].astype(str), panel_df["Entrez_ID"].astype(str)))
        df_in["Entrez_ID"] = df_in["Gene_Symbol"].astype(str).map(sym_to_entrez)

    row_vec = pd.Series(0.0, index=gene_cols)
    matched = 0
    for _, r in df_in.iterrows():
        eid = str(r["Entrez_ID"]).strip()
        if eid in row_vec.index:
            row_vec[eid] = float(r["Log2_CPM_Expression"])
            matched += 1

    print(f"[INFO] Loaded {matched}/20 panel genes from external CSV: {csv_path}")
    row_df = pd.DataFrame([row_vec], columns=gene_cols)
    print_prediction(f"Walk-In Patient ({os.path.basename(csv_path)})", pipe, row_df)


def main():
    print("[INFO] Loading trained 20-gene ALS classifier...")
    pipe, gene_cols, X_all = load_prototype()
    ensure_walkin_template(X_all)

    print(f"[READY] Loaded {len(X_all)} cohort profiles + external walk-in CSV mode.")
    print("Commands:")
    print(f"  - 'csv'                 -> predict from {DEFAULT_WALKIN_CSV}")
    print("  - 'csv path/to/file.csv'-> predict from any custom 20-gene CSV")
    print("  - 'Case19' or 'random'  -> test a GSE234297 sample")
    print("  - 'quit'                -> exit\n")

    while True:
        user_in = input("Enter command > ").strip()
        if not user_in:
            continue
        if user_in.lower() in {"quit", "exit", "q"}:
            print("Exiting prototype. Good luck on Nov 19!")
            break
        if user_in.lower() == "csv":
            predict_from_csv(DEFAULT_WALKIN_CSV, pipe, gene_cols)
        elif user_in.lower().startswith("csv "):
            custom_path = user_in[4:].strip()
            predict_from_csv(custom_path, pipe, gene_cols)
        else:
            query = random.choice(X_all.index.tolist()) if user_in.lower() == "random" else user_in
            matches = [c for c in X_all.index if query.lower() in c.lower()]
            if not matches:
                print(f"  [!] No sample matching '{query}'. Try 'csv', 'Case19', or 'random'.")
                continue
            sample_id = matches[0]
            print_prediction(sample_id, pipe, X_all.loc[[sample_id]])


if __name__ == "__main__":
    main()