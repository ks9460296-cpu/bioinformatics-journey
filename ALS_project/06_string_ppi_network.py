"""
Level-Up #2: Mechanistic Protein-Protein Interaction (PPI) Network via STRING-db
Checks how our top 20 blood biomarkers physically/functionally connect to
core ALS genes (TARDBP/TDP-43, C9ORF72, TIA1, DDX3X, SOD1) and our matched
drug targets (CDC7 for PHA-767491, NFKB1/RELA for Withaferin A, HSPA1A for Celastrol).
"""

import os
import time
import requests
import pandas as pd

OUT_DIR = "als_ideathon_outputs"
PANEL_CSV = os.path.join(OUT_DIR, "top20_biomarker_panel.csv")

CORE_ALS_AND_DRUG_TARGETS = [
    "TARDBP",  # TDP-43 hallmark protein
    "C9ORF72", # Top ALS-SG driver
    "TIA1",    # Stress granule assembly
    "DDX3X",   # Stress granule RNA helicase
    "CDC7",    # Kinase target of PHA-767491
    "NFKB1",   # Pathway target of Withaferin A
    "RELA",    # NF-kB p65 subunit
    "HSPA1A",  # HSP70 target of Celastrol
    "SOD1",    # Classic familial ALS gene
]


def main():
    panel_df = pd.read_csv(PANEL_CSV)
    panel_genes = panel_df["Gene_Symbol"].dropna().astype(str).tolist()
    all_genes = list(dict.fromkeys(panel_genes + CORE_ALS_AND_DRUG_TARGETS))

    print(f"[INFO] Querying STRING-db (Human, taxon 9606) for {len(all_genes)} proteins...")
    payload = {
        "identifiers": "\r".join(all_genes),
        "species": 9606,
        "required_score": 400,  # Medium-to-high confidence (>= 0.400)
        "caller_identity": "als_precision_ideathon",
    }

    # 1. Fetch interaction edges (JSON)
    resp = requests.post("https://string-db.org/api/json/network", data=payload, timeout=30)
    resp.raise_for_status()
    edges = resp.json()

    if not edges:
        print("[WARN] No interactions returned at score >= 0.400.")
        return

    edge_df = pd.DataFrame(
        [
            {
                "Protein_A": e["preferredName_A"],
                "Protein_B": e["preferredName_B"],
                "Combined_Score": e["score"],
            }
            for e in edges
        ]
    ).sort_values("Combined_Score", ascending=False)

    edges_csv = os.path.join(OUT_DIR, "string_ppi_edges.csv")
    edge_df.to_csv(edges_csv, index=False)
    print(f"[INFO] Found {len(edge_df)} interactions (saved to {edges_csv})")

    # Highlight direct links between our 20-gene panel and ALS/drug targets
    panel_set = set(panel_genes)
    target_set = set(CORE_ALS_AND_DRUG_TARGETS)
    bridge = edge_df[
        (edge_df["Protein_A"].isin(panel_set) & edge_df["Protein_B"].isin(target_set))
        | (edge_df["Protein_B"].isin(panel_set) & edge_df["Protein_A"].isin(target_set))
    ]
    print("\n=== DIRECT BRIDGES: 20-Gene Blood Panel <-> ALS & Drug Targets ===")
    if bridge.empty:
        print("  No direct bridges at >= 0.400 (check full edge table).")
    else:
        print(bridge.to_string(index=False))

    # 2. Download high-res STRING network PNG
    time.sleep(1.0)
    img_payload = {
        "identifiers": "\r".join(all_genes),
        "species": 9606,
        "required_score": 400,
        "network_flavor": "confidence",
        "caller_identity": "als_precision_ideathon",
    }
    img_resp = requests.post(
        "https://string-db.org/api/image/network", data=img_payload, timeout=30
    )
    img_resp.raise_for_status()
    img_path = os.path.join(OUT_DIR, "string_ppi_network.png")
    with open(img_path, "wb") as f:
        f.write(img_resp.content)
    print(f"\n[DONE] Saved STRING-db PPI network diagram to {img_path}")


if __name__ == "__main__":
    main()