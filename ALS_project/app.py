"""
ALS Precision Router — Doctor-Friendly Streamlit Web App
Wraps your trained 20-gene ML model (als_subtype_classifier.pkl) in a clean,
drag-and-drop web interface for live ideathon demonstration.

Run in your (.venv) terminal:
    pip install streamlit
    streamlit run app.py
"""

import os
import gzip
import pickle
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="ALS Precision Router",
    page_icon="🧬",
    layout="wide",
)

OUT_DIR = "als_ideathon_outputs"
MODEL_PATH = os.path.join(OUT_DIR, "als_subtype_classifier.pkl")
PANEL_CSV = os.path.join(OUT_DIR, "top20_biomarker_panel.csv")
GZ_PATH = "GSE234297_gene_raw_counts.txt.gz"
WALKIN_CSV = os.path.join(OUT_DIR, "new_walkin_patient.csv")

SUBTYPE_DETAILS = {
    1: {
        "name": "ALS-SG / Interferon-Stress (Subtype 1)",
        "badge": "Stress Granule & Innate Immune",
        "pathway": "Stress Granule Assembly (C9ORF72, TIA1, DDX3X) & Type-I Interferon Signaling",
        "drugs": [
            ("Withaferin A", "Adj. p = 5.82e-8 (Significant)", "NF-κB inhibitor; clears TDP-43 pathology in ALS/FTLD models"),
            ("Celastrol", "Adj. p = 6.19e-4 (Significant)", "HSP70 activator; extends survival in SOD1-G93A ALS mice"),
        ],
    },
    0: {
        "name": "ALS-Ox / Vascular-Immune (Subtype 2)",
        "badge": "Oxidative Stress & Complement",
        "pathway": "Hydrogen Peroxide Catabolic Process (HBM, HBA1, HBQ1) & Complement Activation",
        "drugs": [
            ("PHA-767491", "Adj. p = 0.108 (Exploratory)", "CDC7 kinase inhibitor; blocks pathological TDP-43 phosphorylation"),
            ("Docetaxel", "Adj. p = 0.108 (Exploratory)", "Microtubule-stabilizing candidate from L1000 signature reversal"),
        ],
    },
}


@st.cache_resource
def load_model_and_panel():
    with open(MODEL_PATH, "rb") as f:
        saved = pickle.load(f)
    panel_df = pd.read_csv(PANEL_CSV)
    panel_df["Entrez_ID"] = panel_df["Entrez_ID"].astype(str)
    return saved["pipeline"], saved["gene_columns"], panel_df


@st.cache_data
def load_demo_cases(gene_cols):
    if not os.path.exists(GZ_PATH):
        return pd.DataFrame()
    with gzip.open(GZ_PATH, "rt") as f:
        df = pd.read_csv(f, sep=None, engine="python", index_col=0)
    case_cols = [c for c in df.columns if "case" in c.lower() or "als" in c.lower()]
    df = df[case_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    df.index = df.index.astype(str)
    cpm = df.div(df.sum(axis=0), axis=1) * 1e6
    log_cpm = np.log2(cpm + 1.0)
    return log_cpm.reindex(gene_cols, fill_value=0).T


def predict_from_uploaded_df(df_in: pd.DataFrame, pipe, gene_cols, panel_df):
    if "Log2_CPM_Expression" not in df_in.columns:
        st.error("CSV must contain a 'Log2_CPM_Expression' column (plus 'Entrez_ID' or 'Gene_Symbol').")
        return None

    df_work = df_in.copy()
    if "Entrez_ID" not in df_work.columns:
        sym_to_entrez = dict(zip(panel_df["Gene_Symbol"].astype(str), panel_df["Entrez_ID"].astype(str)))
        df_work["Entrez_ID"] = df_work["Gene_Symbol"].astype(str).map(sym_to_entrez)

    row_vec = pd.Series(0.0, index=gene_cols)
    matched_genes = []
    for _, r in df_work.iterrows():
        eid = str(r.get("Entrez_ID", "")).strip()
        if eid in row_vec.index:
            val = float(r["Log2_CPM_Expression"])
            row_vec[eid] = val
            sym = panel_df.loc[panel_df["Entrez_ID"] == eid, "Gene_Symbol"].values[0]
            matched_genes.append({"Gene": sym, "Log2_CPM": round(val, 3)})

    row_df = pd.DataFrame([row_vec], columns=gene_cols)
    pred = int(pipe.predict(row_df)[0])
    prob_sg = float(pipe.predict_proba(row_df)[0, 1])
    conf = prob_sg if pred == 1 else (1.0 - prob_sg)
    return pred, conf, len(matched_genes), pd.DataFrame(matched_genes)


def render_report(patient_label: str, pred: int, conf: float, matched_count: int, gene_preview: pd.DataFrame):
    info = SUBTYPE_DETAILS[pred]
    st.subheader(f"Clinical Decision Card — {patient_label}")

    if matched_count < 18:
        st.warning(
            f"Only {matched_count}/20 panel genes matched. Ensure sample is Whole Blood "
            "and normalized to Log2(CPM+1) for reliable cross-lab predictions."
        )

    c1, c2, c3 = st.columns(3)
    c1.metric("Predicted Subtype", info["name"].split(" (")[0], info["badge"])
    c2.metric("Model Confidence", f"{conf:.1%}")
    c3.metric("20-Gene Panel Coverage", f"{matched_count} / 20 genes")
    st.progress(min(max(conf, 0.0), 1.0))

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("#### Core Biological Pathway")
        st.info(info["pathway"])

    with col_right:
        st.markdown("#### Matched Repurposed Drugs (LINCS L1000)")
        for drug, p_txt, mech in info["drugs"]:
            st.markdown(f"- **{drug}** ({p_txt}) — {mech}")

    if not gene_preview.empty:
        with st.expander("View Patient's 20-Gene Biomarker Profile"):
            st.dataframe(gene_preview, use_container_width=True)


def main():
    st.title("🧬 ALS Precision Router")
    st.caption(
        "20-Gene Blood Subtype Classifier & Drug-Matching Prototype | "
        "Research Use Only (Trained on NCBI GEO GSE234297, N = 96 sALS)"
    )

    if not os.path.exists(MODEL_PATH):
        st.error(f"Model not found at {MODEL_PATH}. Run 03_train_and_validate_ml.py first.")
        return

    pipe, gene_cols, panel_df = load_model_and_panel()
    demo_cases = load_demo_cases(gene_cols)

    tab1, tab2 = st.tabs(["📤 Upload Patient CSV", "🧪 Quick Test Patient"])

    with tab1:
        if os.path.exists(WALKIN_CSV):
            with open(WALKIN_CSV, "rb") as f:
                st.download_button(
                    "Download Sample 20-Gene CSV Template",
                    data=f,
                    file_name="sample_20gene_patient.csv",
                    mime="text/csv",
                )

        uploaded = st.file_uploader("Upload a patient's 20-gene blood report (.csv)", type=["csv"])
        if uploaded is not None:
            df_up = pd.read_csv(uploaded)
            res = predict_from_uploaded_df(df_up, pipe, gene_cols, panel_df)
            if res is not None:
                pred, conf, m_count, g_df = res
                render_report(uploaded.name, pred, conf, m_count, g_df)

    with tab2:
        if demo_cases.empty:
            st.warning("GSE234297_gene_raw_counts.txt.gz not found in project root.")
        else:
            default_idx = 0
            sample_list = demo_cases.index.tolist()
            for i, s in enumerate(sample_list):
                if "case27" in s.lower():
                    default_idx = i
                    break
            selected = st.selectbox("Select an sALS patient profile:", sample_list, index=default_idx)
            if st.button("Analyze Patient Profile", type="primary"):
                row_df = demo_cases.loc[[selected]]
                pred = int(pipe.predict(row_df)[0])
                prob_sg = float(pipe.predict_proba(row_df)[0, 1])
                conf = prob_sg if pred == 1 else (1.0 - prob_sg)

                panel_ids = panel_df["Entrez_ID"].tolist()
                g_df = pd.DataFrame(
                    {
                        "Gene": panel_df["Gene_Symbol"],
                        "Log2_CPM": [round(float(row_df[eid].values[0]), 3) for eid in panel_ids],
                    }
                )
                render_report(selected, pred, conf, 20, g_df)


if __name__ == "__main__":
    main()