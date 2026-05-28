"""
VersaBank Holdback Model -- Step 3: Validation & Visualizations
================================================================
Produces four charts for the presentation package:
  1. ROC Curve                        -- model discrimination power
  2. Default Rate by Lender Partner   -- portfolio risk segmentation
  3. Coefficient Plot                 -- which features drive default risk
  4. PD Score Distribution            -- how the model separates defaulters
                                         from non-defaulters

All plots are saved to the versabank_holdback folder as PNG files.
"""

import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split

RANDOM_SEED = 42
OUT_DIR = "C:/Users/oblok/Documents/versabank_holdback/"

# ── Plotting style ────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi": 150,
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
})

# ── 1. Load data & model ──────────────────────────────────────────────────────
print("Loading data and model...")
df = pd.read_csv(OUT_DIR + "loan_scores.csv")

with open(OUT_DIR + "sk_model.pkl", "rb") as f:
    sk_model = pickle.load(f)

# Reconstruct X and y for the test set (same split as training step)
drop_cols = ["Default", "Origination_Date", "Origination_Year",
             "Origination_YearMonth", "PD"]
X = df.drop(columns=drop_cols)
y = df["Default"]

_, X_test, _, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_SEED, stratify=y
)
y_prob_test = sk_model.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, y_prob_test)

# ── Chart 1: ROC Curve ────────────────────────────────────────────────────────
print("Plotting ROC Curve...")
fpr, tpr, _ = roc_curve(y_test, y_prob_test)

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(fpr, tpr, color="#1f4e79", lw=2,
        label=f"Logistic Regression (AUC = {roc_auc:.4f})")
ax.plot([0, 1], [0, 1], color="grey", lw=1, linestyle="--", label="Random Classifier")
ax.fill_between(fpr, tpr, alpha=0.08, color="#1f4e79")
ax.set_xlabel("False Positive Rate (1 - Specificity)")
ax.set_ylabel("True Positive Rate (Sensitivity)")
ax.set_title("ROC Curve -- VersaBank Default Model")
ax.legend(loc="lower right")
ax.annotate(f"AUC = {roc_auc:.4f}", xy=(0.6, 0.2),
            fontsize=12, color="#1f4e79", fontweight="bold")
plt.tight_layout()
plt.savefig(OUT_DIR + "chart_01_roc_curve.png")
plt.close()
print(f"  Saved chart_01_roc_curve.png  (AUC = {roc_auc:.4f})")

# ── Chart 2: Default Rate by Lender Partner ───────────────────────────────────
# Reconstruct which partner each loan belongs to from the one-hot columns.
# Partner A is the dropped reference category (drop_first=True in preprocessing).
print("Plotting Default Rate by Lender Partner...")

partner_cols = [c for c in df.columns if c.startswith("Lender_Partner_")]
def get_partner(row):
    for col in partner_cols:
        if row[col] == 1:
            return col.replace("Lender_Partner_", "")
    return "Partner A"   # reference category

df["Partner"] = df.apply(get_partner, axis=1)

partner_stats = (
    df.groupby("Partner")["Default"]
    .agg(["mean", "count"])
    .rename(columns={"mean": "Default_Rate", "count": "Loan_Count"})
    .sort_values("Default_Rate", ascending=False)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(partner_stats["Partner"], partner_stats["Default_Rate"] * 100,
              color="#1f4e79", edgecolor="white", width=0.55)

# Label each bar with the rate and loan count
for bar, (_, row) in zip(bars, partner_stats.iterrows()):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.15,
            f"{row['Default_Rate']*100:.2f}%\n(n={row['Loan_Count']:,})",
            ha="center", va="bottom", fontsize=9, color="#333333")

ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylabel("Observed Default Rate")
ax.set_title("Default Rate by Lender Partner")
ax.set_ylim(0, partner_stats["Default_Rate"].max() * 100 * 1.25)
plt.tight_layout()
plt.savefig(OUT_DIR + "chart_02_default_by_partner.png")
plt.close()
print("  Saved chart_02_default_by_partner.png")

# ── Chart 3: Coefficient Plot (top predictors) ────────────────────────────────
print("Plotting Coefficient Chart...")

coef_df = pd.DataFrame({
    "Feature": X.columns,
    "Coefficient": sk_model.coef_[0]
}).sort_values("Coefficient")

# Show top 10 positive and top 10 negative coefficients
top_n = 12
coef_plot = pd.concat([coef_df.head(top_n), coef_df.tail(top_n)])
colors = ["#c0392b" if c > 0 else "#1f4e79" for c in coef_plot["Coefficient"]]

fig, ax = plt.subplots(figsize=(9, 8))
bars = ax.barh(coef_plot["Feature"], coef_plot["Coefficient"],
               color=colors, edgecolor="white")
ax.axvline(0, color="black", lw=0.8, linestyle="--")
ax.set_xlabel("Coefficient (log-odds of default)")
ax.set_title("Top Predictors of Default Risk\n(Red = increases risk | Blue = reduces risk)")
plt.tight_layout()
plt.savefig(OUT_DIR + "chart_03_coefficients.png")
plt.close()
print("  Saved chart_03_coefficients.png")

# ── Chart 4: PD Score Distribution ───────────────────────────────────────────
print("Plotting PD Distribution...")

defaults     = df[df["Default"] == 1]["PD"]
non_defaults = df[df["Default"] == 0]["PD"]

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(non_defaults, bins=60, alpha=0.6, color="#1f4e79",
        label="No Default (0)", density=True)
ax.hist(defaults, bins=60, alpha=0.6, color="#c0392b",
        label="Default (1)", density=True)
ax.set_xlabel("Predicted Probability of Default (PD)")
ax.set_ylabel("Density")
ax.set_title("PD Score Distribution -- Defaulters vs Non-Defaulters")
ax.legend()
plt.tight_layout()
plt.savefig(OUT_DIR + "chart_04_pd_distribution.png")
plt.close()
print("  Saved chart_04_pd_distribution.png")

print("\nStep 3 complete. All charts saved.")
print(f"  ROC-AUC: {roc_auc:.4f}")
print(f"  Partner default rates:\n{partner_stats[['Partner','Default_Rate','Loan_Count']].to_string(index=False)}")
