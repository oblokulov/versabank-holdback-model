"""
VersaBank Holdback Model -- Step 5: Vintage / Cohort Analysis
==============================================================
Groups loans by origination year (vintage) and analyzes how default rates
evolve across cohorts. This is standard practice in consumer credit portfolios
and directly maps to the JD requirement for "time-series and vintage/cohort
analyses."

Two charts produced:
  Chart 6: Annual default rate by vintage year (bar)
           -- shows which origination years produced the riskiest loans
  Chart 7: Cumulative default rate by vintage (line)
           -- shows how each cohort matures over time (classic vintage curve)

Note: origination dates were simulated uniformly over 2015-2024. In real data,
post-crisis vintages (2009-2012) typically show elevated default rates, and
recent vintages appear healthier simply because they haven't had time to season.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

OUT_DIR = "C:/Users/oblok/Documents/versabank_holdback/"

plt.rcParams.update({
    "figure.dpi": 150,
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
})

# ── 1. Load scored loans ──────────────────────────────────────────────────────
print("Loading data...")
df = pd.read_csv(OUT_DIR + "loan_scores.csv")

# Recover partner labels
partner_cols = [c for c in df.columns if c.startswith("Lender_Partner_")]
def get_partner(row):
    for col in partner_cols:
        if row[col] == 1:
            return col.replace("Lender_Partner_", "")
    return "Partner A"

df["Partner"] = df.apply(get_partner, axis=1)
df["Origination_Date"] = pd.to_datetime(df["Origination_Date"])
df["Vintage_Year"] = df["Origination_Date"].dt.year
df["Vintage_Quarter"] = df["Origination_Date"].dt.to_period("Q").astype(str)

print(f"  Vintage years: {sorted(df['Vintage_Year'].unique())}")

# ── Chart 6: Default Rate by Vintage Year ─────────────────────────────────────
print("Plotting Chart 6: Default rate by vintage year...")

vintage_stats = (
    df.groupby("Vintage_Year")
    .agg(
        Default_Rate=("Default", "mean"),
        Loan_Count=("Default", "count"),
        Avg_PD=("PD", "mean")
    )
    .reset_index()
)

fig, ax1 = plt.subplots(figsize=(10, 5))

# Bar: observed default rate
bars = ax1.bar(vintage_stats["Vintage_Year"],
               vintage_stats["Default_Rate"] * 100,
               color="#1f4e79", width=0.5, label="Observed Default Rate")

# Line overlay: average model PD
ax2 = ax1.twinx()
ax2.plot(vintage_stats["Vintage_Year"],
         vintage_stats["Avg_PD"] * 100,
         color="#c0392b", marker="o", lw=2, ms=6, label="Avg Model PD")
ax2.set_ylabel("Average Model PD (%)", color="#c0392b")
ax2.tick_params(axis="y", labelcolor="#c0392b")
ax2.yaxis.set_major_formatter(mtick.PercentFormatter())

ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
ax1.set_xlabel("Origination Year (Vintage)")
ax1.set_ylabel("Observed Default Rate")
ax1.set_title("Default Rate by Vintage Year\n(Bars = Actual | Line = Model PD)")
ax1.set_xticks(vintage_stats["Vintage_Year"])

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()
plt.savefig(OUT_DIR + "chart_06_vintage_default_rate.png")
plt.close()
print("  Saved chart_06_vintage_default_rate.png")

# ── Chart 7: Cumulative Default Curve by Vintage ──────────────────────────────
# Classic vintage curve: for each cohort, plot the cumulative default rate
# as loans age (measured in months since origination).
# Since defaults are a single snapshot (not time-series), we simulate loan age
# by computing months between origination and a fixed observation date (2025-01-01).
print("Plotting Chart 7: Cumulative vintage curves...")

OBSERVATION_DATE = pd.Timestamp("2025-01-01")
df["Months_On_Book"] = (
    (OBSERVATION_DATE.year - df["Origination_Date"].dt.year) * 12
    + (OBSERVATION_DATE.month - df["Origination_Date"].dt.month)
).clip(lower=1)

# Build cumulative default curve: bucket loans into 12-month age bands
df["Age_Band"] = pd.cut(df["Months_On_Book"],
                         bins=[0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120],
                         labels=["12m", "24m", "36m", "48m", "60m",
                                 "72m", "84m", "96m", "108m", "120m"])

# For each vintage, compute cumulative default rate at each age band
# (assumes defaults observed are cumulative up to observation date)
vintage_age = (
    df.groupby(["Vintage_Year", "Age_Band"], observed=True)["Default"]
    .agg(["sum", "count"])
    .rename(columns={"sum": "Defaults", "count": "Loans"})
    .reset_index()
)

# Cumulative defaults per vintage: sort by age band and cumsum
fig, ax = plt.subplots(figsize=(11, 6))

colors = plt.cm.Blues(np.linspace(0.35, 0.95, len(vintage_stats["Vintage_Year"])))

for color, (vintage, group) in zip(colors, df.groupby("Vintage_Year")):
    # Each vintage: cumulative default rate by months on book
    age_df = (
        group.groupby("Age_Band", observed=True)["Default"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "Defaults", "count": "Loans"})
        .reset_index()
        .sort_values("Age_Band")
    )
    age_df["Cum_Defaults"] = age_df["Defaults"].cumsum()
    age_df["Cum_Default_Rate"] = age_df["Cum_Defaults"] / age_df["Loans"].iloc[0] * 100

    ax.plot(age_df["Age_Band"].astype(str),
            age_df["Cum_Default_Rate"],
            marker="o", ms=4, lw=1.8,
            color=color, label=str(vintage))

ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_xlabel("Loan Age (Months on Book)")
ax.set_ylabel("Cumulative Default Rate")
ax.set_title("Vintage Cumulative Default Curves (2015-2024)\n"
             "Darker = more recent origination year")
ax.legend(title="Vintage", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig(OUT_DIR + "chart_07_vintage_curves.png")
plt.close()
print("  Saved chart_07_vintage_curves.png")

# ── Chart 8: Default Rate Heatmap by Vintage Year x Lender Partner ────────────
print("Plotting Chart 8: Heatmap -- Vintage x Partner...")
import matplotlib.colors as mcolors

pivot = (
    df.groupby(["Vintage_Year", "Partner"])["Default"]
    .mean()
    .unstack("Partner")
    * 100
)

fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(pivot.values, cmap="Blues", aspect="auto")

ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index)
ax.set_xlabel("Lender Partner")
ax.set_ylabel("Vintage Year")
ax.set_title("Default Rate Heatmap: Vintage Year x Lender Partner (%)")

# Annotate each cell
for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        val = pivot.values[i, j]
        ax.text(j, i, f"{val:.1f}%", ha="center", va="center",
                fontsize=8, color="white" if val > pivot.values.mean() else "#1a1a1a")

plt.colorbar(im, ax=ax, label="Default Rate (%)")
plt.tight_layout()
plt.savefig(OUT_DIR + "chart_08_heatmap.png")
plt.close()
print("  Saved chart_08_heatmap.png")

# ── Summary stats ─────────────────────────────────────────────────────────────
print("\nVintage Summary:")
print(vintage_stats[["Vintage_Year", "Default_Rate", "Loan_Count", "Avg_PD"]].to_string(index=False))
print("\nStep 5 complete.")
