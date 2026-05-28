"""
VersaBank Holdback Model -- Step 2: Model Training
====================================================
Loads the preprocessed dataset, performs a stratified 80/20 train-test
split, then fits two models:
  1. sklearn LogisticRegression  -- for fast predict_proba() scoring
  2. statsmodels Logit           -- for the p-value / coefficient table
                                    (required for regulatory defensibility)

Outputs:
  - loan_scores.csv   : every loan with its Probability of Default (PD)
  - model_summary.txt : statsmodels coefficient table
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import statsmodels.api as sm

RANDOM_SEED = 42

# ── 1. Load processed data ────────────────────────────────────────────────────
print("Loading processed data...")
df = pd.read_csv("C:/Users/oblok/Documents/versabank_holdback/processed_loans.csv")
print(f"  Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

# ── 2. Define features (X) and target (y) ────────────────────────────────────
# Drop non-feature columns: the target, the ID-like date fields
drop_cols = ["Default", "Origination_Date", "Origination_Year", "Origination_YearMonth"]
X = df.drop(columns=drop_cols)
y = df["Default"]

print(f"  Features: {X.shape[1]} columns")
print(f"  Target distribution: {y.value_counts().to_dict()}")

# ── 3. Stratified 80/20 train-test split ─────────────────────────────────────
# stratify=y ensures both splits have the same ~11.6% default rate.
# Without this, a random split on imbalanced data can produce a test set
# with very few defaults, making evaluation unreliable.
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=RANDOM_SEED,
    stratify=y
)
print(f"\nTrain size: {X_train.shape[0]:,} | Test size: {X_test.shape[0]:,}")
print(f"  Train default rate: {y_train.mean():.4f}")
print(f"  Test  default rate: {y_test.mean():.4f}")

# ── 4. sklearn LogisticRegression ────────────────────────────────────────────
# class_weight='balanced' corrects for the 88/12 class imbalance by
# up-weighting the minority (default) class during training. Without this,
# the model would learn to predict 0 almost every time and appear accurate.
print("\nFitting sklearn LogisticRegression...")
sk_model = LogisticRegression(
    class_weight="balanced",
    max_iter=1000,
    random_state=RANDOM_SEED,
    solver="lbfgs"
)
sk_model.fit(X_train, y_train)

# Evaluate on held-out test set
y_prob_test = sk_model.predict_proba(X_test)[:, 1]   # probability of default
roc_auc     = roc_auc_score(y_test, y_prob_test)
print(f"  ROC-AUC on test set: {roc_auc:.4f}")

if roc_auc >= 0.70:
    print("  PASS -- model clears the 0.70 threshold for regulatory use")
else:
    print("  WARNING -- ROC-AUC below 0.70, model needs review")

# ── 5. Score every loan in the full dataset ───────────────────────────────────
# We assign a Probability of Default (PD) to every loan, not just the test set,
# because the holdback calculation in Step 4 requires PD for the full portfolio.
print("\nScoring all loans...")
pd_scores = sk_model.predict_proba(X)[:, 1]
df["PD"] = pd_scores
df["Default"] = y.values   # add target back for reference

out_scores = "C:/Users/oblok/Documents/versabank_holdback/loan_scores.csv"
df.to_csv(out_scores, index=False)
print(f"  Saved loan scores -> {out_scores}")

# ── 6. statsmodels Logit (for regulatory-grade output) ───────────────────────
# statsmodels gives us a proper summary table with:
#   - Coefficients (log-odds)
#   - Standard errors
#   - z-scores and p-values
#   - Confidence intervals
# This is what you show in a model documentation package to risk / compliance.
print("\nFitting statsmodels Logit (this may take ~60s on 200k rows)...")

# statsmodels requires an explicit intercept column
X_train_sm = sm.add_constant(X_train.astype(float))

sm_model = sm.Logit(y_train.astype(float), X_train_sm)
sm_result = sm_model.fit(method="lbfgs", maxiter=1000, disp=False)

# Print summary to console
print(sm_result.summary2())

# Save summary to text file for the documentation package
summary_path = "C:/Users/oblok/Documents/versabank_holdback/model_summary.txt"
with open(summary_path, "w") as f:
    f.write(str(sm_result.summary2()))
print(f"\nSaved statsmodels summary -> {summary_path}")

# Save sklearn model for reuse in later steps
model_path = "C:/Users/oblok/Documents/versabank_holdback/sk_model.pkl"
with open(model_path, "wb") as f:
    pickle.dump(sk_model, f)
print(f"Saved sklearn model -> {model_path}")

print("\nStep 2 complete.")
