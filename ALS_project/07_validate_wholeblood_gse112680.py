"""
Level-Up #3: Matched Whole-Blood External Cohort Validation (NCBI GEO GSE112680)
- Downloads GSE112680_series_matrix.txt.gz (376 Whole-Blood samples, Netherlands)
  and official NCBI platform annotation GPL10558.annot.gz (~8 MB).
- Filters specifically to confirmed ALS patients (excluding controls & ALS-mimics).
- Maps Illumina HumanHT-12 V4 probes (ILMN_*) to our 20-gene Entrez IDs.
- Applies cross-platform Z-score alignment to GSE234297's training scale and runs
  als_subtype_classifier.pkl to check cross-country whole-blood generalization!
"""

import os
import gzip
import pickle
import urllib.request
import numpy as np
import pandas as pd

OUT_DIR = "als_ideathon_outputs"
MODEL_PATH = os.path.join(OUT_DIR, "als_subtype_classifier.pkl")
PANEL_CSV = os.path.join(OUT_DIR, "top20_biomarker_panel.csv")
GZ_TRAIN = "GSE234297_gene_raw_counts.txt.gz"

MATRIX_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE112nnn/"
    "GSE112680/matrix/GSE112680_series_matrix.txt.gz"
)
ANNOT_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPL10nnn/"
    "GPL10558/annot/GPL10558.annot.gz"
)
LOCAL_MATRIX = "GSE112680_series_matrix.txt.gz"
LOCAL_ANNOT = "GPL10558.annot.gz"


def download_if_missing(url: str, dest: str):
    if os.path.exists(dest):
        print(f"[INFO] Found local file: {dest}")
        return
    print(f"[INFO] Downloading {dest} from NCBI GEO...")
    urllib.request.urlretrieve(url, dest)
    print(f"[INFO] Saved {dest}")


def load_gpl10558_mapping(panel_eids: set) -> dict:
    """Map Entrez_ID -> list of ILMN_ probes using NCBI's official GPL10558.annot.gz."""
    skip = 0
    with gzip.open(LOCAL_ANNOT, "rt", errors="replace") as f:
        for idx, line in enumerate(f):
            if line.startswith("!platform_table_begin"):
                skip = idx + 1
                break

    annot = pd.read_csv(
        LOCAL_ANNOT,
        compression="gzip",
        sep="\t",
        skiprows=skip,
        comment="!",
        low_memory=False,
    )
    # Find ID column and Gene ID column
    id_col = "ID"
    gene_id_col = [c for c in annot.columns if "gene id" in c.lower()][0]

    eid_to_probes = {}
    for _, row in annot[[id_col, gene_id_col]].dropna().iterrows():
        probe = str(row[id_col]).strip()
        # Gene ID can have /// for multi-mapping probes
        for part in str(row[gene_id_col]).split("///"):
            eid = part.strip().split(".")[0]
            if eid in panel_eids:
                eid_to_probes.setdefault(eid, []).append(probe)
    return eid_to_probes


def get_train_stats(panel_eids: list):
    """Get mean and std of the 20 panel genes in GSE234297 for cross-platform alignment."""
    with gzip.open(GZ_TRAIN, "rt") as f:
        df = pd.read_csv(f, sep=None, engine="python", index_col=0)
    case_cols = [c for c in df.columns if "case" in c.lower() or "als" in c.lower()]
    df = df[case_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    df.index = df.index.astype(str)
    cpm = df.div(df.sum(axis=0), axis=1) * 1e6
    log_cpm = np.log2(cpm + 1.0)
    sub = log_cpm.reindex(panel_eids, fill_value=0)
    return sub.mean(axis=1), sub.std(axis=1) + 1e-8


def parse_gse112680_als():
    """Parse sample metadata and expression matrix from GSE112680_series_matrix.txt.gz."""
    titles = []
    char_rows = []
    data_start = 0

    with gzip.open(LOCAL_MATRIX, "rt", errors="replace") as f:
        for idx, line in enumerate(f):
            clean = line.rstrip("\r\n")
            if clean.startswith("!Sample_title"):
                titles = [x.strip('"') for x in clean.split("\t")[1:]]
            elif clean.startswith("!Sample_characteristics_ch1"):
                char_rows.append([x.strip('"') for x in clean.split("\t")[1:]])
            elif clean.startswith("!series_matrix_table_begin"):
                data_start = idx + 1
                break

    expr = pd.read_csv(
        LOCAL_MATRIX,
        compression="gzip",
        sep="\t",
        skiprows=data_start,
        comment="!",
        index_col=0,
    )
    expr.index = expr.index.astype(str).str.strip('"')
    expr.columns = [str(c).strip('"') for c in expr.columns]

    # Combine title + all characteristics per sample to detect confirmed ALS
    als_cols = []
    for i, col in enumerate(expr.columns):
        meta_parts = []
        if i < len(titles):
            meta_parts.append(titles[i])
        for crow in char_rows:
            if i < len(crow):
                meta_parts.append(crow[i])
        meta_str = " | ".join(meta_parts).lower()

        is_als = ("als" in meta_str) and ("mimic" not in meta_str) and ("control" not in meta_str)
        if is_als:
            als_cols.append(col)

    print(f"[INFO] GSE112680 total samples: {expr.shape[1]} | Confirmed ALS whole-blood: {len(als_cols)}")
    return expr[als_cols].apply(pd.to_numeric, errors="coerce")


def main():
    download_if_missing(MATRIX_URL, LOCAL_MATRIX)
    download_if_missing(ANNOT_URL, LOCAL_ANNOT)

    with open(MODEL_PATH, "rb") as f:
        saved = pickle.load(f)
    pipe = saved["pipeline"]
    gene_cols = saved["gene_columns"]

    panel_df = pd.read_csv(PANEL_CSV)
    panel_eids = panel_df["Entrez_ID"].astype(str).tolist()

    eid_to_probes = load_gpl10558_mapping(set(panel_eids))
    expr_als = parse_gse112680_als()
    train_mean, train_std = get_train_stats(panel_eids)

    matched_eids = {}
    for eid in panel_eids:
        probes = [p for p in eid_to_probes.get(eid, []) if p in expr_als.index]
        if probes:
            matched_eids[eid] = expr_als.loc[probes].mean(axis=0)

    print(f"[INFO] Matched {len(matched_eids)}/20 panel genes in GSE112680 Whole Blood")
    panel_mat = pd.DataFrame(matched_eids).T  # genes x patients

    # Cross-platform Z-score alignment onto GSE234297 scale
    ext_mean = panel_mat.mean(axis=1)
    ext_std = panel_mat.std(axis=1) + 1e-8
    aligned = panel_mat.sub(ext_mean, axis=0).div(ext_std, axis=0)
    for eid in aligned.index:
        aligned.loc[eid] = aligned.loc[eid] * train_std[eid] + train_mean[eid]

    X_ext = pd.DataFrame(0.0, index=aligned.columns, columns=gene_cols)
    for eid in aligned.index:
        X_ext[eid] = aligned.loc[eid].values

    preds = pipe.predict(X_ext)
    probs = pipe.predict_proba(X_ext)[:, 1]

    n_sg = int((preds == 1).sum())
    n_ox = int((preds == 0).sum())
    total = len(preds)

    print("\n=== EXTERNAL WHOLE-BLOOD VALIDATION (GSE112680, NETHERLANDS) ===")
    print(f"  Total ALS Whole-Blood Patients: {total}")
    print(f"  Predicted ALS-SG (Subtype 1):   {n_sg} ({n_sg / total:.1%})")
    print(f"  Predicted ALS-Ox (Subtype 2):   {n_ox} ({n_ox / total:.1%})")
    print(f"  Mean SG Probability:            {probs.mean():.3f}")

    out_csv = os.path.join(OUT_DIR, "gse112680_wholeblood_predictions.csv")
    pd.DataFrame(
        {
            "Sample": X_ext.index,
            "Predicted_Subtype": ["ALS-SG" if p == 1 else "ALS-Ox" for p in preds],
            "Prob_ALS_SG": np.round(probs, 4),
        }
    ).to_csv(out_csv, index=False)
    print(f"[DONE] Saved predictions to {out_csv}")


if __name__ == "__main__":
    main()