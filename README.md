# VersaBank Dynamic Holdback Model

A full credit risk pipeline built to estimate partner-level holdback requirements
for a loan receivables portfolio, aligned to VersaBank's Receivable Purchase Program (RPP).

## What This Does

Takes raw loan data and produces a recommended holdback percentage for each
lending partner using the industry-standard Expected Loss formula:

**EL = PD × EAD × LGD**

- **PD** — Probability of Default (logistic regression model)
- **EAD** — Exposure at Default (outstanding loan balance)
- **LGD** — Loss Given Default (assumed 50%, Basel II conservative floor)

A variance buffer is added on top of Expected Loss to cover unexpected
macroeconomic shocks. The final output is a partner-level holdback percentage
backed by a statistically validated model (ROC-AUC: 0.7531).

## Pipeline Overview

| Step | File | Description |
|---|---|---|
| 1 | `01_preprocessing.py` | Data cleaning, encoding, winsorization, standardization |
| 2 | `02_model_training.py` | Logistic regression (sklearn + statsmodels) |
| 3 | `03_validation_visuals.py` | ROC curve, coefficient plot, PD distribution |
| 4 | `04_holdback_calculation.py` | EL formula, variance buffer, holdback by partner |
| 5 | `05_vintage_cohort.py` | 10-year vintage/cohort analysis and heatmap |

Full notebook: `versabank_holdback_model.ipynb`

## Key Results

- **ROC-AUC:** 0.7531 (industry minimum: 0.70)
- **Strongest default predictors:** Interest rate, unemployment, loan amount
- **Holdback range:** 23.01% (Partner D) to 23.54% (Partner E)
- **Highest risk concentration:** Partner E × 2024 vintage (13.2% default rate)

## Dataset

Real-world loan dataset sourced from Kaggle (255,347 records, 18 features).
The raw CSV is not included in this repo due to file size.

## Tools

Python 3.14 · pandas · scikit-learn · statsmodels · matplotlib

## Status

Work in progress — approximately one week of development (May 22–28, 2026).
Current limitations and next steps are documented in `doc_02_results_and_reflection_v2.md`.
