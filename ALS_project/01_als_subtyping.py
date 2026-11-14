"""
Precision ALS Stratification & Subtype-Specific DEG Pipeline (Day 1 Prototype)
Dataset: NCBI GEO GSE234297 (96 sporadic ALS + 48 healthy control whole-blood RNA-seq)
URL: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE234297

Requirements:
    pip install pandas numpy scipy scikit-learn matplotlib seaborn
"""

import os
import gzip
import urllib.request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

DATA_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE234nnn/"
    "GSE234297/suppl/GSE234297_gene_raw_counts.txt.gz"
)
LOCAL_GZ = "GSE234297_gene_raw_counts.txt.gz"
OUT_DIR = "als_ideathon_outputs"
os.makedirs(OUT_DIR, exist_ok=True)


def download_gse234297(url: str = DATA_URL, dest: str = LOCAL_GZ) -> str:
    if os.path.exists(dest):
        print(f"[INFO] Found local dataset: {dest}")
        return dest
    print("[INFO] Downloading GSE234297 raw counts (~4.9 MB) from NCBI GEO...")
    urllib.request.urlretrieve(url, dest)
    print(f"[INFO] Saved to {dest}")
    return dest


def bh_fdr(pvals: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg FDR adjustment."""
    n = len(pvals)
    order = np.argsort(pvals)
    ranked = pvals[order]
    fdr = ranked * n / (np.arange(1, n + 1))
    fdr = np.minimum.accumulate(fdr[::-1])[::-1]
    fdr = np.clip(fdr, 0.0, 1.0)
    out = np.empty_like(fdr)
    out[order] = fdr
    return out


def load_and_normalize(gz_path: str):
    with gzip.open(gz_path, "rt") as f:
        df = pd.read_csv(f, sep=None, engine="python", index_col=0)

    print(f"[INFO] Raw matrix shape: {df.shape[0]} genes x {df.shape[1]} samples")

    case_cols = [c for c in df.columns if "case" in c.lower() or "als" in c.lower()]
    ctrl_cols = [c for c in df.columns if "control" in c.lower() or "ctrl" in c.lower()]

    if not case_cols or not ctrl_cols:
        raise ValueError(
            "Could not auto-detect Case/Control columns. "
            f"Sample columns preview: {list(df.columns[:5])}"
        )

    print(f"[INFO] Detected {len(case_cols)} sALS cases and {len(ctrl_cols)} controls")
    df = df[case_cols + ctrl_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    min_samples = int(0.20 * df.shape[1])
    keep_mask = (df >= 10).sum(axis=1) >= min_samples
    df_filt = df.loc[keep_mask].copy()
    print(f"[INFO] Genes after low-expression filter: {df_filt.shape[0]}")

    lib_sizes = df_filt.sum(axis=0)
    cpm = df_filt.div(lib_sizes, axis=1) * 1e6
    log_cpm = np.log2(cpm + 1.0)

    return log_cpm, case_cols, ctrl_cols


def cluster_sals_patients(log_cpm: pd.DataFrame, case_cols: list):
    als_expr = log_cpm[case_cols]
    gene_var = als_expr.var(axis=1)
    top_genes = gene_var.nlargest(2000).index
    X = als_expr.loc[top_genes].T

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=15, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    best_k, best_score, best_labels = 3, -1.0, None
    print("\n[INFO] Evaluating molecular subtype clusters (k = 2 to 5):")
    for k in range(2, 6):
        km = KMeans(n_clusters=k, n_init=50, random_state=42)
        labels = km.fit_predict(X_pca[:, :10])
        score = silhouette_score(X_pca[:, :10], labels)
        print(f"  k = {k} -> Silhouette Score = {score:.4f}")
        if score > best_score:
            best_k, best_score, best_labels = k, score, labels

    print(f"[RESULT] Optimal clusters: k = {best_k} (Silhouette = {best_score:.4f})")

    cluster_df = pd.DataFrame(
        {
            "Sample": case_cols,
            "Subtype": [f"ALS-Subtype-{c + 1}" for c in best_labels],
            "PC1": X_pca[:, 0],
            "PC2": X_pca[:, 1],
        }
    )
    cluster_df.to_csv(os.path.join(OUT_DIR, "sals_subtype_assignments.csv"), index=False)

    plt.figure(figsize=(8, 6), dpi=150)
    sns.scatterplot(
        data=cluster_df,
        x="PC1",
        y="PC2",
        hue="Subtype",
        palette="viridis",
        s=75,
        alpha=0.9,
        edgecolor="white",
    )
    var1, var2 = pca.explained_variance_ratio_[:2] * 100
    plt.title(f"Sporadic ALS Blood Transcriptomic Subtypes (GSE234297, k={best_k})")
    plt.xlabel(f"PC1 ({var1:.1f}% variance)")
    plt.ylabel(f"PC2 ({var2:.1f}% variance)")
    plt.legend(title="Molecular Subtype", frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "als_subtypes_pca.png"))
    plt.close()

    return cluster_df


def compute_subtype_degs(log_cpm: pd.DataFrame, cluster_df: pd.DataFrame, ctrl_cols: list):
    ctrl_mat = log_cpm[ctrl_cols].values
    genes = log_cpm.index.to_numpy()

    for subtype, grp in cluster_df.groupby("Subtype"):
        sub_cols = grp["Sample"].tolist()
        sub_mat = log_cpm[sub_cols].values

        log2fc = sub_mat.mean(axis=1) - ctrl_mat.mean(axis=1)
        _, pvals = stats.ttest_ind(sub_mat, ctrl_mat, axis=1, equal_var=False)
        pvals = np.nan_to_num(pvals, nan=1.0)
        fdr = bh_fdr(pvals)

        deg_df = pd.DataFrame(
            {"Gene": genes, "log2FC": log2fc, "pval": pvals, "FDR": fdr}
        ).sort_values("FDR")

        deg_df.to_csv(os.path.join(OUT_DIR, f"{subtype}_DEGs_vs_Control.csv"), index=False)

        sig = deg_df[deg_df["FDR"] < 0.05]
        up_genes = sig[sig["log2FC"] > 0].nlargest(150, "log2FC")["Gene"].tolist()
        down_genes = sig[sig["log2FC"] < 0].nsmallest(150, "log2FC")["Gene"].tolist()

        with open(os.path.join(OUT_DIR, f"{subtype}_L1000_up.txt"), "w") as f:
            f.write("\n".join(map(str, up_genes)))
        with open(os.path.join(OUT_DIR, f"{subtype}_L1000_down.txt"), "w") as f:
            f.write("\n".join(map(str, down_genes)))

        print(
            f"[INFO] {subtype} (n={len(sub_cols)}): "
            f"{len(sig)} FDR<0.05 DEGs | Exported {len(up_genes)} Up / {len(down_genes)} Down for CMap"
        )


def plot_tdp43_panel(log_cpm: pd.DataFrame, cluster_df: pd.DataFrame, ctrl_cols: list):
    target_genes = [
        "TARDBP", "STMN2", "UNC13A", "ELAVL3", "NEFL", "SOD1", "FUS", "C9orf72",
        "SQSTM1", "OPTN", "TBK1", "CHMP2B"
    ]
    present = [g for g in target_genes if g in log_cpm.index]
    if len(present) < 3:
        print("[WARN] Fewer than 3 curated ALS/TDP-43 symbols matched index (check Ensembl vs Symbol IDs).")
        return

    group_means = {"Healthy_Control": log_cpm.loc[present, ctrl_cols].mean(axis=1)}
    for subtype, grp in cluster_df.groupby("Subtype"):
        group_means[subtype] = log_cpm.loc[present, grp["Sample"].tolist()].mean(axis=1)

    heatmap_df = pd.DataFrame(group_means)
    heatmap_z = heatmap_df.sub(heatmap_df.mean(axis=1), axis=0).div(
        heatmap_df.std(axis=1) + 1e-8, axis=0
    )

    plt.figure(figsize=(8, 5), dpi=150)
    sns.heatmap(heatmap_z, cmap="RdBu_r", center=0, annot=True, fmt=".2f", linewidths=0.5)
    plt.title("ALS & TDP-43 Pathway Gene Expression Across Blood Subtypes (Z-score)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "subtype_tdp43_heatmap.png"))
    plt.close()
    print(f"[INFO] Saved TDP-43 panel heatmap for {len(present)} genes.")


if __name__ == "__main__":
    gz_file = download_gse234297()
    log_cpm_df, als_samples, control_samples = load_and_normalize(gz_file)
    clusters = cluster_sals_patients(log_cpm_df, als_samples)
    compute_subtype_degs(log_cpm_df, clusters, control_samples)
    plot_tdp43_panel(log_cpm_df, clusters, control_samples)
    print(f"\n[DONE] All Day-1 outputs saved in ./{OUT_DIR}/")