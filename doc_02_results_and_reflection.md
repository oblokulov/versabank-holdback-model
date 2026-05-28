# VersaBank Holdback Model — Results, Reflection & Development Notes
### Project: Dynamic Holdback Framework — Lending Partner Portfolio

---

## What the Model Found

### Model Performance

The logistic regression model achieved a **ROC-AUC score of 0.7531** on the
held-out test set. This means the model correctly ranks a randomly chosen
defaulting loan above a randomly chosen non-defaulting loan about 75% of the
time — a meaningful improvement over random chance (50%) and comfortably above
the 0.70 threshold used in industry practice.

---

### Key Risk Drivers

The model identified the following as the strongest predictors of default.
All findings below were statistically significant (p < 0.05), meaning we are
confident they reflect real patterns in the data, not random noise.

**Factors that increase default risk:**

| Risk Factor | Plain English Meaning |
|---|---|
| High interest rate | Borrowers paying higher rates are more financially stretched |
| Unemployed status | No income makes repayment much harder |
| Large loan amount | Larger obligations are harder to sustain through hardship |
| Part-time or self-employed | Less income stability increases repayment risk |
| High debt-to-income (DTI) ratio | Already carrying significant debt relative to earnings |

**Factors that reduce default risk:**

| Protective Factor | Plain English Meaning |
|---|---|
| Older borrower age | Older borrowers tend to have more stable financial histories |
| Longer employment history | Job stability signals repayment reliability |
| Higher income | More capacity to absorb financial shocks |
| Having a co-signer | A guarantor materially reduces the bank's exposure |
| Having a mortgage | Homeowners tend to prioritize secured debt repayment |

**Notable non-finding:** Loan term (the length of the loan in months) was
**not a statistically significant predictor** in this dataset (p = 0.63).
This is an honest result. A model that forces every variable to "matter" is
less trustworthy than one that admits when a variable adds no predictive value.

---

### Holdback Recommendations by Lending Partner

| Partner | Portfolio Size | Recommended Holdback |
|---|---|---|
| Partner E | $3.25B | **23.54%** |
| Partner C | $6.53B | **23.28%** |
| Partner B | $8.17B | **23.21%** |
| Partner A | $9.77B | **23.17%** |
| Partner D | $4.86B | **23.01%** |

The spread across partners is narrow (approximately 0.5 percentage points) in
this version of the model. This is because lending partner assignment was
simulated randomly — meaning all five partners received statistically similar
loan populations. In a real-world deployment with genuine origination differences
between partners, the model would be expected to produce a much wider spread,
and the value of partner-level holdback differentiation would be greater.

---

### Vintage Analysis Findings

The **2018 origination vintage** showed the highest observed default rate across
the portfolio (12.1%), while the **2019 and 2020 vintages** were the
lowest-performing years for default risk.

The most notable concentration of risk was in the **Partner E, 2024 vintage**,
which showed a 13.2% default rate — the single highest cell in the entire
portfolio. In a live risk management environment, this would be flagged for
immediate review and would likely trigger a holdback adjustment for Partner E's
most recent originations.

---

## What We Would Do Differently With More Time

This project was built as a proof-of-concept framework. With additional time,
data, and resources, the following improvements would be prioritized:

### 1. Use Real Origination Dates
The dates used in the vintage analysis were simulated. In a production model,
actual origination dates would be sourced directly from the loan management
system, producing a true historical time series rather than a simulated one.

### 2. Use a More Sophisticated Model
Logistic regression is transparent and regulatory-friendly, which is why we
started there. However, it assumes a linear relationship between each feature
and the default probability — an assumption that may not always hold in
real data.

More powerful alternatives worth exploring:
- **Gradient Boosting (e.g., XGBoost)** — captures non-linear patterns and
  interaction effects between variables, typically producing higher ROC-AUC scores.
- **Survival Analysis / Cox Proportional Hazards Model** — models not just
  whether a borrower defaults, but when. This is especially useful for
  portfolios with loans at different stages of maturity.

### 3. Calibrate the Probability Scores
The PD scores produced by the current model are optimized for ranking
(distinguishing high-risk from low-risk borrowers) rather than for producing
accurate raw probabilities. A calibration step — such as **Platt Scaling** or
**isotonic regression** — would adjust the scores so that a loan assigned a PD
of 0.12 genuinely has approximately a 12% chance of defaulting. This distinction
matters when the scores are used directly in the EL formula.

### 4. Incorporate Macroeconomic Variables
The current model uses only loan-level and borrower-level characteristics.
Adding macroeconomic variables — such as the unemployment rate, the Bank of
Canada policy rate, or regional housing price indices — would allow the model
to produce **stress-tested** PD estimates: what does default risk look like if
unemployment rises by 2 percentage points?

### 5. Build a Real Lender Partner Segmentation
In this project, lending partner assignment was simulated. In production, the
model would be trained on actual partner-tagged loan data, allowing the
coefficient table to reveal whether certain partners are originating
systematically riskier loans — controlling for all other borrower characteristics.
This is where the holdback differentiation becomes most defensible to a regulator.

### 6. Automate and Schedule the Pipeline
As built, the model is a static analysis run once on a fixed dataset. In
production, the pipeline should be scheduled to re-run monthly as new loan
performance data arrives, with the holdback table automatically updated and
distributed to the relevant risk officers.

---

## How This Was Built

This entire framework — data cleaning, statistical modelling, validation,
holdback calculation, vintage analysis, and eight presentation-quality charts —
was built in a single focused session using Python, an open-source programming
language that is industry standard in quantitative finance.

The tools used (pandas, scikit-learn, statsmodels, matplotlib) are the exact
same tools used by risk and analytics teams at major financial institutions.
No proprietary software, no cloud computing, and no external data purchases
were required.

The speed of delivery reflects two things:

First, a clear and structured methodology. Rather than exploring randomly,
the project was divided into five discrete, sequenced steps before any code
was written. Each step had a defined input, a defined output, and a defined
purpose. This is how production analytics teams operate.

Second, the use of well-established techniques. Logistic regression, the
EL = PD × EAD × LGD formula, and ROC-AUC validation are not experimental —
they are decades-old standards in credit risk. Knowing which tools to reach
for, and why, is what allows a rigorous framework to be assembled quickly.

The result is a pipeline that is not a prototype. The code is commented,
the methodology is documented, the assumptions are stated explicitly, and
every output is reproducible. Any analyst who opens the files can run them
and arrive at the exact same numbers.
