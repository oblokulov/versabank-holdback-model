# VersaBank Dynamic Holdback Model — What We Built and Why
### Prepared for: Tim
### Status: Work in Progress — Initial Framework (as of May 28, 2026)

---

## Background and Timeline

On **May 22nd**, following an initial meeting with Lauren, I began organizing the
data and mapping out the structure of this project. The goal was to build a
statistical framework that could help VersaBank determine how large a financial
cushion — called a **holdback** — should be held against each lending partner's
portfolio.

A holdback is money the bank sets aside as protection. When VersaBank purchases
loan receivables from a lending partner through its **Receivable Purchase Program
(RPP)**, it takes on the risk that some of those borrowers will stop paying.
The holdback is the buffer that absorbs those losses if they materialize.

After the initial planning session, it became clear that the model needed to be
built specifically around the RPP structure — not just general loan default
risk. That required rethinking parts of the approach and sourcing additional
context about how VersaBank's RPP agreements are structured, what data is
available at the point of purchase, and what a "loss" actually means in that
context.

Following the meeting with **Tim on May 26th**, further adjustments were made to
align the framework with the priorities discussed. This document reflects the
current state of the model as of May 28th — approximately one week into
development.

This is an early-stage framework. It is directionally correct and
methodologically sound, but it is not yet production-ready. The limitations are
explained clearly at the end of this document.

---

## The Problem We Were Solving

When VersaBank purchases receivables from lending partners, it needs to answer
one question:

> "Of the loans we are buying from this partner — how many will stop paying,
> and how much money do we stand to lose?"

The holdback is the bank's answer to that question turned into a dollar amount.
Instead of holding the same percentage back from every partner regardless of
their risk profile, this framework attempts to make that number **dynamic** —
meaning it adjusts based on the actual risk characteristics of each partner's
loan portfolio.

---

## What We Built — Step by Step

### Step 1 — Organizing the Data

We started with a dataset of **255,347 loan records**, each describing a single
borrower: their credit score, income, loan size, employment status, whether they
had a co-signer, and several other characteristics. Each loan was also marked
with whether it ultimately defaulted (the borrower stopped paying).

Before the data could be used for modelling, it needed to be cleaned. This
involved three things:

- **Removing extreme outliers** — a small number of loans had unrealistically
  high income or loan values that would distort the model. We capped these at
  the 99th percentile, a standard technique called **winsorization**.

- **Putting numbers on the same scale** — interest rates (e.g. 8%) and loan
  amounts (e.g. $50,000) cannot be fed into a model without adjustment, because
  the model would treat the larger number as more important simply because it is
  bigger. We normalized all continuous numbers to a common scale.

- **Converting text into numbers** — the model cannot read words like "Full-time"
  or "Business." We converted these categories into a series of 0s and 1s,
  which the model can process.

We also added two pieces of information that were missing from the raw data:

- **Lending partner labels** — to make the holdback calculation work at the
  partner level, each loan was assigned to one of five lending partners.
  In the current version, this assignment is simulated. In the next version,
  this would be replaced by actual partner IDs from VersaBank's RPP records.

- **Origination dates** — to enable time-based analysis, we simulated loan
  origination dates spanning January 2015 to December 2024, giving us a
  ten-year view of the portfolio.

---

### Step 2 — Building the Statistical Model

With clean data, we built a **logistic regression** model. This is one of the
most widely used and regulatorily accepted tools in credit risk — banks have
used it for decades because it is transparent and auditable. You can see exactly
which factors the model relies on and how much weight it gives to each one.

The model reads the characteristics of each loan and outputs a
**Probability of Default (PD)** — a number between 0 and 1 representing the
estimated likelihood that a borrower will stop making payments.

The model was trained on 80% of the data and tested on the remaining 20%
(a held-back **test set** it had never seen). This prevents the model from
simply memorizing the training data — a problem known as **overfitting** — and
ensures the results would hold up on new loans.

---

### Step 3 — Checking If the Model Works

We measured model performance using the **ROC-AUC score** — a standard metric
in credit risk that measures how well the model separates borrowers who will
default from those who will not. It ranges from 0.50 (no better than random)
to 1.00 (perfect).

**Our model scored 0.7531**, which clears the 0.70 industry threshold for a
model to be considered statistically useful.

We also produced a formal coefficient table using a statistical package called
**statsmodels**, which shows which borrower characteristics are significant
predictors of default and which are not. This is the type of output a risk
committee or regulator would review.

---

### Step 4 — Calculating the Holdback

A probability score does not mean anything on its own to a finance team.
We converted it into a dollar amount using the **Expected Loss formula**:

```
Expected Loss (EL) = Probability of Default (PD)
                   x Exposure at Default (EAD)
                   x Loss Given Default (LGD)
```

- **PD** — from our model
- **EAD** — the outstanding loan balance (we used the original loan amount)
- **LGD** — assumed at 50%, meaning the bank recovers half the value of a
  defaulted loan. This is a conservative placeholder based on Basel II norms.
  In production, this would be estimated from VersaBank's actual recovery data.

We then added a **variance buffer** — an extra reserve to cover unexpected
losses caused by events like a sudden rise in unemployment or a recession.
This buffer is calculated from the statistical spread of losses within each
partner's portfolio.

The final holdback for each partner is:
```
Holdback % = (Expected Loss + Variance Buffer) / Total Portfolio Outstanding
```

---

### Step 5 — Analyzing Trends Over Time (Vintage Analysis)

Finally, we conducted a **vintage analysis** — grouping loans by the year they
were originally issued and tracking how their default rates evolved over time.

This is standard practice in consumer credit risk. Loans issued in certain
economic environments tend to perform differently than those issued in others.
By tracking this over ten years of simulated originations, we can identify
which lending periods produced the highest-risk loans — and factor that into
the holdback recommendation.

---

## Current Limitations

This model has been in development for approximately one week. It is a working
framework, not a finished product. The following are known gaps that would be
addressed before any production deployment:

1. **Lending partner data is simulated.** The model cannot currently
   differentiate between partners in a statistically meaningful way because
   the partner labels were randomly assigned. Real partner-tagged RPP data
   would allow the model to identify whether certain partners are consistently
   originating riskier receivables.

2. **The LGD assumption is a placeholder.** Assuming 50% recovery is
   conservative and standard, but VersaBank's actual recovery rates on
   purchased receivables may differ significantly. Replacing this with
   empirical recovery data would make the holdback calculations more accurate.

3. **Origination dates are simulated.** The vintage analysis is illustrative.
   Actual origination dates from RPP transaction records would make this
   analysis real and actionable.

4. **The model has not been calibrated.** The PD scores are useful for
   ranking loans by risk but currently overstate raw probabilities. A
   calibration step is needed before the scores can be used as literal
   default probability estimates in the EL formula.

These are expected limitations at this stage of development. The framework,
methodology, and code are all in place — closing these gaps is a data and
time problem, not a modelling problem.
