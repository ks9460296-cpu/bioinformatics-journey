Precision ALS Stratification & Subtype-Matched Drug Repurposing

A bioinformatics and machine learning prototype that stratifies sporadic Amyotrophic Lateral Sclerosis (sALS) patients from peripheral blood RNA-seq, compresses the signature to a 20-gene diagnostic panel, and matches each molecular subtype to repurposed therapeutic candidates.

Disclaimer: Research prototype built for the November 19, 2026 Ideathon. Not intended for clinical diagnosis or treatment decisions.

Problem & Solution

The Problem: ~90% of ALS cases are sporadic with high molecular heterogeneity, yet clinical trials often treat all patients identically—diluting true drug responders.

Our Solution: A closed-loop blood-to-drug router that clusters blood transcriptomes into distinct molecular subtypes, trains a 20-gene supervised classifier, and pairs each subtype with LINCS L1000 signature-reversing compounds.

Key Results (NCBI GEO GSE234297, N = 96 sALS + 48 Controls)

Unsupervised Blood Subtyping (01_als_subtyping.py): PC1 captures 52.7% of transcriptomic variance, separating sporadic ALS patients into two subtypes:

ALS-SG / Interferon-Stress: Enriched for Defense Response to Virus ($\text{Adj. } p = 2.58 \times 10^{-6}$) and Stress Granule Assembly (C9ORF72, TIA1, DDX3X; $\text{Adj. } p = 2.32 \times 10^{-4}$).

ALS-Ox / Vascular-Immune: Enriched for Hydrogen Peroxide Catabolic Process (HBM, HBA1, HBQ1; $\text{Adj. } p = 2.26 \times 10^{-5}$) and Complement Activation.

Subtype-Specific Drug Repurposing (02_map_and_repurpose.py):

ALS-SG matched Withaferin A ($\text{Adj. } p = 5.82 \times 10^{-8}$) and Celastrol ($\text{Adj. } p = 6.19 \times 10^{-4}$).

ALS-Ox pointed to exploratory candidates including PHA-767491 ($\text{Adj. } p = 0.108$) and Docetaxel.

20-Gene Supervised ML Classifier (03_train_and_validate_ml.py): Zero-leakage 80/20 split Logistic Regression compressed 13,211 genes to 20 biomarkers (led by TTBK2, KLHL9, RAB3GAP2, FMR1), achieving 0.996 5-fold CV ROC-AUC (94.8% accuracy) and 1.000 hold-out ROC-AUC (20/20 unseen patients).

External Cross-Cohort Stress Test (05_test_external_gse115259.py): Evaluated 11 Italian PBMC samples from GSE115259 (16/20 genes matched), demonstrating how PBMC vs. whole-blood tissue differences and sequencer batch effects shift predictions—highlighting the need for matched whole-blood protocols and batch correction.

Project Structure

01_als_subtyping.py — Downloads GSE234297, normalizes counts ($\log_2(\text{CPM}+1)$), clusters sALS patients, and exports DEGs.

02_map_and_repurpose.py — Maps Entrez IDs to HGNC symbols via MyGene.info and queries Enrichr (GO BP & LINCS L1000).

03_train_and_validate_ml.py — Trains and validates the 20-gene classifier (als_subtype_classifier.pkl).

04_predict_patient_demo.py — Interactive CLI prototype for walk-in 20-gene CSVs and cohort samples.

05_test_external_gse115259.py — External validation script for GSE115259_RAW.tar.

app.py — Doctor-friendly Streamlit web dashboard for CSV upload and instant subtype/drug reporting.

Quickstart

python3 -m venv .venv
source .venv/bin/activate
pip install pandas numpy scipy scikit-learn matplotlib seaborn requests streamlit

python 01_als_subtyping.py
python 02_map_and_repurpose.py
python 03_train_and_validate_ml.py
streamlit run app.py


Author

Keshav Sharma 