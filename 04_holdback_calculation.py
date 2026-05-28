"""
VersaBank Holdback Model -- Step 4: Holdback Calculation
=========================================================
Translates model output (Probability of Default) into a dollar-denominated
Expected Loss estimate, then adds a variance buffer to produce a recommended
holdback percentage for each lending partner.

Formula:
    EL  = PD x EAD x LGD
    where:
        PD  = Probability of Default  (from logistic regression)
        EAD = Exposure at Default     (outstanding LoanAmount, pre-standardization)
        LGD = Loss Given Default      (assumed 50% -- standard Basel II floor)

Holdback % per partner:
    Holdback = (Sum of EL + Variance Buffer) / Total Portfolio EAD
    Buffer   = 1 standard deviation of loan-level EL within the partner portfolio
               (covers unexpected loss from macroeconomic shocks)

Outputs:
    - holdback_table.csv       : per-partner holdback recommendation
    - chart_05_holdback.png    : bar chart of holdback % by partner
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

LGD     = 0.50          # Loss Given Default assumption (50% recovery rate)
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
print("Loading loan scores...")
df = pd.read_csv(OUT_DIR + "loan_scores.csv")
print(f"  {df.shape[0]:,} loans loaded")

# ── 2. Recover original (un-standardized) LoanAmount for EAD ─────────────────
# StandardScaler transformed LoanAmount in preprocessing. For EAD we need
# actual dollar values. We reload the raw file and merge on row index.
print("Recovering original loan amounts for EAD...")
raw = pd.read_csv("C:/Users/oblok/Downloads/Loan_default.csv")[["LoanAmount"]]
raw.columns = ["EAD"]        # EAD = outstanding principal (Exposure at Default)
df["EAD"] = raw["EAD"].values
print(f"  EAD range: ${df['EAD'].min():,.0f} -- ${df['EAD'].max():,.0f}")

# ── 3. Reconstruct Lender_Partner label ──────────────────────────────────────
partner_cols = [c for c in df.columns if c.startswith("Lender_Partner_")]

def get_partner(row):
    for col in partner_cols:
        if row[col] == 1:
            return col.replace("Lender_Partner_", "")
    return "Partner A"    # reference category (dropped during one-hot encoding)

print("Reconstructing partner labels...")
df["Partner"] = df.apply(get_partner, axis=1)

# ── 4. Calculate Expected Loss per loan ───────────────────────────────────────
# EL = PD x EAD x LGD
# This is the dollar amount the bank expects to lose on each loan.
df["EL"] = df["PD"] * df["EAD"] * LGD
print(f"\nPortfolio-level Expected Loss: ${df['EL'].sum():,.0f}")
print(f"As % of total EAD:            {df['EL'].sum() / df['EAD'].sum() * 100:.2f}%")

# ── 5. Aggregate by partner and compute holdback ──────────────────────────────
print("\nCalculating holdback by partner...")

results = []
for partner, group in df.groupby("Partner"):
    total_ead        = group["EAD"].sum()
    total_el         = group["EL"].sum()

    # Variance buffer: 1 standard deviation of loan-level EL within the partner.
    # This absorbs unexpected loss spikes (e.g., a recession hitting one sector).
    el_std           = group["EL"].std()
    n_loans          = len(group)
    variance_buffer  = el_std * np.sqrt(n_loans)   # portfolio-level std dev

    total_requirement = total_el + variance_buffer

    el_pct           = total_el / total_ead * 100
    buffer_pct       = variance_buffer / total_ead * 100
    holdback_pct     = total_requirement / total_ead * 100

    results.append({
        "Partner"           : partner,
        "Loan_Count"        : n_loans,
        "Total_EAD"         : total_ead,
        "Expected_Loss"     : total_el,
        "EL_Pct"            : el_pct,
        "Variance_Buffer"   : variance_buffer,
        "Buffer_Pct"        : buffer_pct,
        "Total_Requirement" : total_requirement,
        "Holdback_Pct"      : holdback_pct,
    })

holdback_df = pd.DataFrame(results).sort_values("Holdback_Pct", ascending=False)

# ── 6. Print the final table ──────────────────────────────────────────────────
print("\n" + "="*75)
print("VERSABANK HOLDBACK RECOMMENDATION TABLE")
print("="*75)
display_cols = ["Partner", "Loan_Count", "Total_EAD",
                "EL_Pct", "Buffer_Pct", "Holdback_Pct"]

for _, row in holdback_df.iterrows():
    print(f"\n  Partner           : {row['Partner']}")
    print(f"  Loans             : {row['Loan_Count']:,}")
    print(f"  Total EAD         : ${row['Total_EAD']:,.0f}")
    print(f"  Expected Loss     : ${row['Expected_Loss']:,.0f}  ({row['EL_Pct']:.2f}% of EAD)")
    print(f"  Variance Buffer   : ${row['Variance_Buffer']:,.0f}  ({row['Buffer_Pct']:.2f}% of EAD)")
    print(f"  --> HOLDBACK REC  : {row['Holdback_Pct']:.2f}% of outstanding portfolio")
print("\n" + "="*75)

# ── 7. Save holdback table ────────────────────────────────────────────────────
holdback_df.to_csv(OUT_DIR + "holdback_table.csv", index=False)
print(f"Saved holdback_table.csv")

# ── 8. Chart: Holdback % by Partner (stacked: EL + Buffer) ───────────────────
print("Plotting holdback chart...")
hdf = holdback_df.sort_values("Holdback_Pct", ascending=True)

fig, ax = plt.subplots(figsize=(9, 5))

bars_el  = ax.barh(hdf["Partner"], hdf["EL_Pct"],
                   color="#1f4e79", label="Expected Loss (EL)")
bars_buf = ax.barh(hdf["Partner"], hdf["Buffer_Pct"],
                   left=hdf["EL_Pct"],
                   color="#c0392b", alpha=0.75, label="Variance Buffer")

# Label each bar with the final holdback %
for _, row in hdf.iterrows():
    ax.text(row["Holdback_Pct"] + 0.05, row["Partner"],
            f"  {row['Holdback_Pct']:.2f}%",
            va="center", fontsize=10, fontweight="bold", color="#1a1a1a")

ax.xaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_xlabel("Holdback as % of Partner Portfolio EAD")
ax.set_title("Recommended Holdback % by Lender Partner\n"
             "(Expected Loss + Variance Buffer)")
ax.legend(loc="lower right")
ax.set_xlim(0, hdf["Holdback_Pct"].max() * 1.25)
plt.tight_layout()
plt.savefig(OUT_DIR + "chart_05_holdback.png")
plt.close()
print("Saved chart_05_holdback.png")

print("\nStep 4 complete.")
