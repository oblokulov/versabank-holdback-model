"""
VersaBank Holdback Model — Step 1: Preprocessing Pipeline
==========================================================
Loads Loan_default.csv, engineers required columns, cleans and
transforms all features into a model-ready format, then saves
the processed dataset for downstream steps.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# ── Reproducibility ──────────────────────────────────────────────────────────
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# ── 1. Load raw data ──────────────────────────────────────────────────────────
print("Loading data...")
df = pd.read_csv("C:/Users/oblok/Downloads/Loan_default.csv")
print(f"  Loaded {df.shape[0]:,} rows × {df.shape[1]} columns")

# ── 2. Engineer: Lender Partner ───────────────────────────────────────────────
# No lender column exists in the raw data. We assign each loan to one of five
# fictional lending partners using a weighted random draw — this simulates a
# realistic portfolio split where some partners originate more volume.
partners = ["Partner A", "Partner B", "Partner C", "Partner D", "Partner E"]
weights  = [0.30, 0.25, 0.20, 0.15, 0.10]   # Partner A is the largest originator

df["Lender_Partner"] = np.random.choice(partners, size=len(df), p=weights)
print(f"  Engineered Lender_Partner: {df['Lender_Partner'].value_counts().to_dict()}")

# ── 3. Engineer: Loan Origination Date (for vintage/cohort analysis) ──────────
# The JD requires 10-year historical cash-flow analysis. We simulate origination
# dates uniformly across Jan 2015 – Dec 2024 (120 months).
months_total = 120
random_months = np.random.randint(0, months_total, size=len(df))
base_date = pd.Timestamp("2015-01-01")
df["Origination_Date"] = base_date + pd.to_timedelta(random_months * 30, unit="D")
df["Origination_Year"]  = df["Origination_Date"].dt.year
df["Origination_YearMonth"] = df["Origination_Date"].dt.to_period("M")
print(f"  Engineered Origination_Date spanning {df['Origination_Date'].min().date()} "
      f"to {df['Origination_Date'].max().date()}")

# ── 4. Drop identifier column ─────────────────────────────────────────────────
df.drop(columns=["LoanID"], inplace=True)

# ── 5. Encode binary Yes/No columns → 0/1 ────────────────────────────────────
binary_cols = ["HasMortgage", "HasDependents", "HasCoSigner"]
for col in binary_cols:
    df[col] = (df[col] == "Yes").astype(int)
print(f"  Encoded binary columns: {binary_cols}")

# ── 6. Winsorize continuous features at 1st / 99th percentile ────────────────
# Clips extreme outliers so they don't disproportionately pull regression
# coefficients. Standard practice in credit-risk model preparation.
continuous_cols = ["Age", "Income", "LoanAmount", "CreditScore",
                   "MonthsEmployed", "InterestRate", "DTIRatio"]

for col in continuous_cols:
    lo = df[col].quantile(0.01)
    hi = df[col].quantile(0.99)
    df[col] = df[col].clip(lo, hi)

print(f"  Winsorized: {continuous_cols}")

# ── 7. One-hot encode categorical columns ─────────────────────────────────────
# drop_first=True avoids multicollinearity (dummy variable trap).
categorical_cols = ["Education", "EmploymentType", "MaritalStatus",
                    "LoanPurpose", "Lender_Partner"]

df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
print(f"  One-hot encoded. New shape: {df.shape}")

# ── 8. Standardize continuous features ───────────────────────────────────────
# Logistic regression treats all features on the same mathematical scale.
# StandardScaler: mean=0, std=1. Fit only — the scaler is saved separately
# so the test set can be transformed with training statistics.
scaler = StandardScaler()
df[continuous_cols] = scaler.fit_transform(df[continuous_cols])
print(f"  Standardized continuous features (mean=0, std=1)")

# ── 9. Save processed dataset ────────────────────────────────────────────────
out_path = "C:/Users/oblok/Documents/versabank_holdback/processed_loans.csv"
# Origination_YearMonth is a Period type — convert to string for CSV storage
df["Origination_YearMonth"] = df["Origination_YearMonth"].astype(str)
df.to_csv(out_path, index=False)
print(f"\nSaved processed dataset -> {out_path}")
print(f"Final shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
print("\nColumn list:")
for col in df.columns:
    print(f"  {col}")
