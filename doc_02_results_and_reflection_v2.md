# VersaBank Dynamic Holdback Model — Results, Limitations & Next Steps
### Status: Week 1 — Initial Framework (May 22 – May 28, 2026)

---

## Context

This project started on **May 22nd** after an initial meeting with Lauren.
The first few days were spent organizing the data, understanding the structure
of VersaBank's **Receivable Purchase Program (RPP)**, and planning the
modelling approach. After realizing the framework needed to be specifically
calibrated around the RPP — not just general loan default prediction — the
scope was refined.

Following the meeting with **Tim on May 26th**, additional adjustments were
made to the direction of the model. As of May 28th, approximately one week of
active development has gone into this framework.

The results below are honest. Where the model performs well, that is noted.
Where the data or method reveals weaknesses, those are explained clearly —
because a model that hides its own limitations is far more dangerous than
one that acknowledges them.

---

## What the Model Got Right

### Model Discrimination

The logistic regression model achieved a **ROC-AUC score of 0.7531** on the
held-out test set. This means the model correctly identifies a high-risk loan
as riskier than a low-risk loan approximately 75% of the time. The industry
minimum for a credit risk model to be considered usable is 0.70. We are above
that threshold.

### Direction of Risk Drivers

The model identified the following as statistically significant predictors
of default. The direction of each finding makes intuitive sense:

**Factors that increase default risk:**
- High interest rate (strongest signal in the model)
- Unemployed borrower status
- Large loan amount relative to the borrower's profile
- Part-time or self-employed income

**Factors that reduce default risk:**
- Older borrower age (strongest protective signal)
- Longer employment history
- Higher income
- Having a co-signer on the loan
- Owning a home (mortgage present)

These findings are directionally consistent with what credit risk theory
would predict, which gives us some confidence that the model is picking
up real patterns rather than noise.

---

## Where the Model Is Weak — And Why

This section is the most important one. After one week of development, the
data reveals several concrete problems that would need to be resolved before
this framework could be used to make real holdback decisions.

---

### Weakness 1 — The PD Scores Are Inflated and Not Calibrated

The average **Probability of Default (PD)** score assigned by the model
across the portfolio is **43%**. The actual default rate in the dataset is
**11.6%**. That is a gap of more than 30 percentage points.

This means the model is systematically overstating how risky loans are.
A loan that the model labels as having a 43% chance of defaulting actually
defaults at a rate closer to 9–10%.

This can be seen directly in the data:

| Model PD Range | Actual Default Rate |
|---|---|
| 0% – 11% | 1.4% actual |
| 11% – 21% | 2.6% actual |
| 39% – 49% | 9.2% actual |
| 86% – 96% | 55.4% actual |

In every single bucket, the model's predicted probability is significantly
higher than what actually happens. This is called a **calibration problem** —
the model ranks loans correctly (higher-risk loans do default more), but the
raw numbers cannot be taken at face value.

**Why this happened:** We used a technique called `class_weight='balanced'`
to handle the fact that only 11.6% of loans defaulted. This helped the model
find patterns in the minority class (defaulters), but it shifted all scores
upward in the process. A **calibration step** (Platt Scaling or isotonic
regression) would correct this, but it has not been done yet.

**Impact on the holdback:** Because the EL formula uses PD directly
(`EL = PD × EAD × LGD`), the overinflated PD scores produce holdback
percentages of approximately **23%** — which is significantly higher than
what a calibrated model would likely produce. These numbers should not be
used for actual holdback decisions without calibration.

---

### Weakness 2 — The Model Cannot Differentiate Between Lending Partners

The single most important output of this framework is a **different holdback
percentage for each lending partner**. That is the whole point.

The current spread across all five partners is:

| Partner | Holdback % |
|---|---|
| Partner E | 23.54% |
| Partner C | 23.28% |
| Partner B | 23.21% |
| Partner A | 23.17% |
| Partner D | 23.01% |

The difference between the highest and lowest recommendation is
**0.53 percentage points**. That is not a meaningful distinction. In practice,
a holdback framework would be expected to produce spreads of several percentage
points between partners — enough to actually influence business decisions.

The statistical test confirms this: in the regression model, **none of the
lending partner variables are statistically significant**. Their p-values
range from 0.17 to 0.87 — well above the 0.05 threshold needed to conclude
that a variable is a real predictor.

| Partner Variable | p-value | Statistically Significant? |
|---|---|---|
| Partner B | 0.87 | No |
| Partner C | 0.59 | No |
| Partner D | 0.73 | No |
| Partner E | 0.17 | No |

**Why this happened:** The lending partner labels were randomly assigned to
loans. The model correctly found that random labels have no predictive power.
This is actually the model behaving correctly — but it exposes the core data
gap: we do not yet have real RPP partner-tagged loan data. Once actual
originator IDs from VersaBank's RPP records are incorporated, partner-level
differentiation should emerge naturally.

---

### Weakness 3 — Loan Term Has No Predictive Power

Intuitively, the length of a loan (12, 24, 36, 48, or 60 months) should
influence the likelihood of default. Longer loans carry more time for
something to go wrong.

The model found that **Loan Term is not statistically significant**
(p-value = 0.627, coefficient ≈ 0.0002). This is an unexpectedly weak
signal, and it is worth investigating. It may reflect a genuine characteristic
of this dataset, or it may mean that loan term is correlated with other
variables (like loan amount or interest rate) in a way that cancels out its
independent effect.

---

### Weakness 4 — Loan Purpose Has Weak and Inconsistent Signals

**Loan Purpose** (Auto, Business, Education, Home, Other) was expected to
be a meaningful predictor. Home loans, for instance, tend to be lower risk
because borrowers are motivated to protect their property.

The model did find that **Home loans** are significantly less likely to default
(p < 0.001). However, **Education loans** (p = 0.61) and **Other loans**
(p = 0.58) showed no statistically significant relationship with default at all.

This inconsistency may be a dataset issue — the loan purpose categories in
this dataset may not map cleanly onto the RPP receivable types that VersaBank
actually purchases.

---

### Weakness 5 — Credit Score Is Weaker Than Expected

In most credit risk models, **credit score** is the single strongest predictor
of default. It is the variable that lenders have relied on most for decades.

In this model, credit score has a coefficient of **-0.122** — which is
statistically significant, but relatively small. It ranks 8th in importance
out of 28 variables. Age (coefficient -0.585) and Interest Rate
(coefficient +0.459) are both far stronger predictors.

This may be a characteristic of this specific dataset, or it may reflect the
fact that credit score is already partially captured by other variables
(income, employment status, DTI ratio) that are also in the model. In a
production model, this would warrant a deeper investigation to understand
whether credit score is being appropriately weighted.

---

### Weakness 6 — The Model Explains Only 12% of Variation in Defaults

The **Pseudo R-squared** — a measure of how much of the variation in default
outcomes the model can explain — is **0.119**, or approximately 12%.

This means 88% of what determines whether a borrower defaults is not captured
by the variables in this dataset. That is not unusual for a one-week-old
logistic regression — but it is a reminder that the model is a starting point,
not a finished answer. Adding macroeconomic variables, payment behaviour data,
and RPP-specific features would meaningfully improve this number.

---

## What We Would Do Differently

Given more time and access to VersaBank's actual RPP data, the following
changes would be the priority:

1. **Replace simulated partner data with real RPP originator IDs.** This is
   the most important fix. Without it, the partner-level holdback
   differentiation — the whole purpose of this framework — cannot function.

2. **Calibrate the PD scores.** Apply Platt Scaling or isotonic regression
   to bring the model's probability estimates in line with actual default
   rates. This is a prerequisite for using the EL formula accurately.

3. **Source actual LGD from VersaBank's recovery data.** The 50% assumption
   is a placeholder. Real recovery rates on RPP receivables may be higher or
   lower, and the holdback should reflect that.

4. **Add a time-based repayment variable.** The dataset captures whether a
   loan defaulted, but not when. A **survival model** (Cox Proportional
   Hazards) would model the timing of default, which is particularly valuable
   for RPP portfolios where cash flow timing matters as much as loss severity.

5. **Incorporate macroeconomic variables.** Unemployment rate, interest rate
   environment, and regional economic conditions all influence default rates
   in ways that borrower-level data alone cannot capture. Adding these would
   improve both predictive power and the stress-testing capability of the
   variance buffer.

---

## Summary

This is one week of work on a problem that a dedicated credit risk team would
spend months on. The framework is in place, the methodology is sound, and the
code is clean and reproducible. But the data gaps — particularly the absence
of real RPP partner data and uncalibrated PD scores — mean the specific
numbers should be treated as illustrative rather than actionable at this stage.

The honest assessment: the model correctly identifies which types of borrowers
are riskier, and the overall pipeline from raw data to holdback recommendation
works end to end. What it cannot yet do is meaningfully differentiate between
lending partners — and that is the core deliverable. Closing that gap is the
next priority.
