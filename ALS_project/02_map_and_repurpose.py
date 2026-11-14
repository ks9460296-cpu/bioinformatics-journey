"""
Step 2: Entrez-to-Symbol Mapping + Pathway & LINCS L1000 Drug Repurposing
Uses MyGene.info (https://mygene.info) and Enrichr (https://maayanlab.cloud/Enrichr)

Install extra dependency once:
    pip install requests
"""

import os
import json
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt

OUT_DIR = "als_ideathon_outputs"


def map_entrez_to_symbol(entrez_ids: list) -> dict:
    """Batch-convert NCBI Entrez IDs to official HGNC gene symbols via MyGene.info."""
    mapping = {}
    batch_size = 500
    for i in range(0, len(entrez_ids), batch_size):
        batch = [str(x).strip() for x in entrez_ids[i : i + batch_size]]
        resp = requests.post(
            "https://mygene.info/v3/gene",
            data={"ids": ",".join(batch), "fields": "symbol"},
            timeout=30,
        )
        resp.raise_for_status()
        for item in resp.json():
            q = str(item.get("query", ""))
            sym = item.get("symbol")
            if sym:
                mapping[q] = sym
    return mapping


def query_enrichr(gene_symbols: list, description: str, libraries: list) -> dict:
    """Submit a gene symbol list to Enrichr and fetch enrichment results."""
    add_url = "https://maayanlab.cloud/Enrichr/addList"
    payload = {
        "list": (None, "\n".join(gene_symbols)),
        "description": (None, description),
    }
    resp = requests.post(add_url, files=payload, timeout=30)
    resp.raise_for_status()
    user_list_id = resp.json()["userListId"]

    results = {}
    for lib in libraries:
        time.sleep(0.5)
        e_url = f"https://maayanlab.cloud/Enrichr/enrich?userListId={user_list_id}&backgroundType={lib}"
        r = requests.get(e_url, timeout=30)
        r.raise_for_status()
        rows = r.json().get(lib, [])
        # Enrichr row format: [rank, term, pval, zscore, combined_score, overlap_genes, adj_pval, ...]
        parsed = [
            {
                "Term": row[1],
                "P_value": row[2],
                "Combined_Score": row[4],
                "Overlap_Genes": ", ".join(row[5]),
                "Adj_P_value": row[6],
            }
            for row in rows[:10]
        ]
        results[lib] = pd.DataFrame(parsed)
    return results


def main():
    subtypes = ["ALS-Subtype-1", "ALS-Subtype-2"]
    summary_rows = []

    for sub in subtypes:
        up_file = os.path.join(OUT_DIR, f"{sub}_L1000_up.txt")
        down_file = os.path.join(OUT_DIR, f"{sub}_L1000_down.txt")
        if not os.path.exists(up_file):
            print(f"[WARN] Missing {up_file}, skipping {sub}")
            continue

        with open(up_file) as f:
            up_ids = [line.strip() for line in f if line.strip()]
        with open(down_file) as f:
            down_ids = [line.strip() for line in f if line.strip()]

        print(f"\n=== Processing {sub} ({len(up_ids)} Up IDs, {len(down_ids)} Down IDs) ===")
        id_map = map_entrez_to_symbol(up_ids + down_ids)

        up_syms = [id_map[i] for i in up_ids if i in id_map]
        down_syms = [id_map[i] for i in down_ids if i in id_map]

        with open(os.path.join(OUT_DIR, f"{sub}_symbols_up.txt"), "w") as f:
            f.write("\n".join(up_syms))
        with open(os.path.join(OUT_DIR, f"{sub}_symbols_down.txt"), "w") as f:
            f.write("\n".join(down_syms))

        print(f"[INFO] Mapped {len(up_syms)} Up symbols, {len(down_syms)} Down symbols")
        print(f"       Sample Up symbols: {up_syms[:8]}")

        # 1) Biological pathways for Up-regulated genes
        if len(up_syms) >= 5:
            up_res = query_enrichr(
                up_syms,
                f"{sub}_UP",
                ["GO_Biological_Process_2023", "LINCS_L1000_Chem_Pert_down"],
            )
            for lib, df_res in up_res.items():
                out_csv = os.path.join(OUT_DIR, f"{sub}_UP_{lib}.csv")
                df_res.to_csv(out_csv, index=False)
                if not df_res.empty:
                    top_term = df_res.iloc[0]
                    print(f"  [Top {lib}] {top_term['Term']} (adj.p={top_term['Adj_P_value']:.2e})")
                    if "LINCS" in lib:
                        for _, r in df_res.head(5).iterrows():
                            summary_rows.append(
                                {
                                    "Subtype": sub,
                                    "Direction_Reversed": "Up-genes reversed by drug",
                                    "Drug_Perturbation": r["Term"],
                                    "Combined_Score": r["Combined_Score"],
                                    "Adj_P_value": r["Adj_P_value"],
                                }
                            )

        # 2) Drugs that reverse Down-regulated genes (LINCS_L1000_Chem_Pert_up)
        if len(down_syms) >= 5:
            down_res = query_enrichr(
                down_syms,
                f"{sub}_DOWN",
                ["LINCS_L1000_Chem_Pert_up"],
            )
            df_d = down_res["LINCS_L1000_Chem_Pert_up"]
            df_d.to_csv(os.path.join(OUT_DIR, f"{sub}_DOWN_LINCS_up.csv"), index=False)
            if not df_d.empty:
                print(f"  [Top LINCS_L1000_Chem_Pert_up] {df_d.iloc[0]['Term']} (adj.p={df_d.iloc[0]['Adj_P_value']:.2e})")

    if summary_rows:
        sum_df = pd.DataFrame(summary_rows)
        sum_df.to_csv(os.path.join(OUT_DIR, "TOP_REPURPOSED_DRUGS_SUMMARY.csv"), index=False)

        # Plot top 5 candidate drugs per subtype
        fig, axes = plt.subplots(1, len(subtypes), figsize=(12, 5), dpi=150)
        if len(subtypes) == 1:
            axes = [axes]
        for ax, sub in zip(axes, subtypes):
            sub_df = sum_df[sum_df["Subtype"] == sub].head(5)
            if sub_df.empty:
                continue
            labels = [f"{'-'.join(t.split('-')[1:-1])} ({t.split(' ')[1]})" for t in sub_df["Drug_Perturbation"]]
            ax.barh(labels[::-1], sub_df["Combined_Score"].values[::-1], color="#3186ff")
            ax.set_title(f"{sub}: Top Reversing Drugs")
            ax.set_xlabel("Enrichr Combined Score")
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, "repurposed_drugs_by_subtype.png"))
        plt.close()
        print(f"\n[DONE] Saved TOP_REPURPOSED_DRUGS_SUMMARY.csv and repurposed_drugs_by_subtype.png in ./{OUT_DIR}/")


if __name__ == "__main__":
    main()