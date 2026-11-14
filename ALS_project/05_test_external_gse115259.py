"""
Step 5: External Cross-Cohort Validation on NCBI GEO GSE115259 (Italy PBMC RNA-seq)
- Automatically locates GSE115259_RAW.tar (in current folder or Windows Downloads).
- Extracts each patient's raw count file, normalizes to log2(CPM+1), maps gene IDs
  to our 20-gene biomarker panel, saves external CSVs (Case97+), and predicts subtypes!
"""

import os
import glob
import gzip
import tarfile
import pickle
import requests
import numpy as np
import pandas as pd

OUT_DIR = "als_ideathon_outputs"
MODEL_PATH = os.path.join(OUT_DIR, "als_subtype_classifier.pkl")
PANEL_CSV = os.path.join(OUT_DIR, "top20_biomarker_panel.csv")
EXT_DIR = os.path.join(OUT_DIR, "external_gse115259")
os.makedirs(EXT_DIR, exist_ok=True)


def find_tar_file() -> str:
    candidates = [
        "GSE115259_RAW.tar",
        os.path.expanduser("~/Downloads/GSE115259_RAW.tar"),
    ] + glob.glob("/mnt/c/Users/*/Downloads/GSE115259_RAW.tar")
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        "Could not find GSE115259_RAW.tar. Drag it into ALS_project/ or check Downloads."
    )


def map_ids_to_entrez(raw_ids: list, panel_df: pd.DataFrame) -> dict:
    """Map Ensembl/Symbol/Entrez IDs from external file to our 20-gene Entrez IDs."""
    sample_id = str(raw_ids[0]).split(".")[0]
    sym_to_entrez = dict(zip(panel_df["Gene_Symbol"].astype(str), panel_df["Entrez_ID"].astype(str)))

    # Case 1: Already Entrez IDs
    if sample_id.isdigit():
        return {str(i): str(i) for i in panel_df["Entrez_ID"]}

    # Case 2: Ensembl IDs (ENSG...) -> query MyGene.info for our 20 symbols/entrez
    if sample_id.upper().startswith("ENSG"):
        entrez_list = panel_df["Entrez_ID"].astype(str).tolist()
        resp = requests.post(
            "https://mygene.info/v3/gene",
            data={"ids": ",".join(entrez_list), "fields": "ensembl.gene,symbol"},
            timeout=20,
        )
        resp.raise_for_status()
        ens_to_entrez = {}
        for item in resp.json():
            eid = str(item.get("query", ""))
            ens = item.get("ensembl", {})
            if isinstance(ens, list):
                for e in ens:
                    if "gene" in e:
                        ens_to_entrez[e["gene"]] = eid
            elif isinstance(ens, dict) and "gene" in ens:
                ens_to_entrez[ens["gene"]] = eid
        return ens_to_entrez

    # Case 3: Gene Symbols
    return sym_to_entrez


def main():
    tar_path = find_tar_file()
    print(f"[INFO] Found external dataset: {tar_path}")

    with open(MODEL_PATH, "rb") as f:
        saved = pickle.load(f)
    pipe = saved["pipeline"]
    gene_cols = saved["gene_columns"]
    panel_df = pd.read_csv(PANEL_CSV)
    panel_df["Entrez_ID"] = panel_df["Entrez_ID"].astype(str)

    SUBTYPE_NAMES = {
        1: "ALS-SG / Interferon-Stress (Subtype 1)",
        0: "ALS-Ox / Vascular-Immune (Subtype 2)",
    }

    with tarfile.open(tar_path, "r") as tar:
        members = [m for m in tar.getmembers() if m.isfile()]
        print(f"[INFO] Found {len(members)} patient files inside GSE115259_RAW.tar")

        id_map = None
        case_num = 97

        for m in members:
            f_obj = tar.extractfile(m)
            if f_obj is None:
                continue

            # Read .gz or plain .txt count file
            if m.name.endswith(".gz"):
                with gzip.open(f_obj, "rt") as gz:
                    df_p = pd.read_csv(gz, sep=None, engine="python", index_col=0)
            else:
                df_p = pd.read_csv(f_obj, sep=None, engine="python", index_col=0)

            # Use first numeric column as counts
            num_cols = df_p.select_dtypes(include=[np.number]).columns
            if len(num_cols) == 0:
                continue
            counts = df_p[num_cols[0]].astype(float)
            counts.index = [str(i).split(".")[0] for i in counts.index]

            # Remove summary rows like __no_feature if present
            counts = counts[~counts.index.str.startswith("__")]
            total_reads = counts.sum()
            if total_reads <= 0:
                continue

            if id_map is None:
                id_map = map_ids_to_entrez(counts.index.tolist(), panel_df)

            # Normalize to log2(CPM + 1)
            log_cpm = np.log2((counts / total_reads) * 1e6 + 1.0)

            # Build 20-gene vector + full feature row for pipeline
            row_vec = pd.Series(0.0, index=gene_cols)
            matched_rows = []
            for raw_id, eid in id_map.items():
                if raw_id in log_cpm.index and eid in row_vec.index:
                    val = float(log_cpm[raw_id])
                    row_vec[eid] = val
                    sym = panel_df.loc[panel_df["Entrez_ID"] == eid, "Gene_Symbol"].values[0]
                    matched_rows.append(
                        {"Gene_Symbol": sym, "Entrez_ID": eid, "Log2_CPM_Expression": round(val, 3)}
                    )

            # Export clean 20-gene CSV as Case97, Case98, ...
            out_csv = os.path.join(EXT_DIR, f"Case{case_num}_{os.path.basename(m.name).split('.')[0]}.csv")
            pd.DataFrame(matched_rows).to_csv(out_csv, index=False)

            row_df = pd.DataFrame([row_vec], columns=gene_cols)
            pred = int(pipe.predict(row_df)[0])
            prob_sg = float(pipe.predict_proba(row_df)[0, 1])
            conf = prob_sg if pred == 1 else (1.0 - prob_sg)

            print(
                f"Case{case_num} ({os.path.basename(m.name)}) | "
                f"Matched {len(matched_rows)}/20 genes -> "
                f"{SUBTYPE_NAMES[pred]} ({conf:.1%} confidence)"
            )
            case_num += 1

    print(f"\n[DONE] Saved external Case97+ CSVs in ./{EXT_DIR}/")


if __name__ == "__main__":
    main()