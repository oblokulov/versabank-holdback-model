# VersaBank Holdback Model — What We Built and Why
### Prepared for: Tim
### Project: Dynamic Holdback Framework — Lending Partner Portfolio

---

## The Problem We Were Solving

When VersaBank lends money through outside lending partners, there is always a risk
that some borrowers will stop making payments. If too many borrowers default at once,
the bank could be left holding losses it was not prepared for.

To protect against this, VersaBank holds back a portion of the funds owed to each
lending partner. This is called a **holdback** — it is essentially a financial
cushion that sits on the bank's balance sheet until it is confident the loans are
performing as expected.

The question this project answers is:

> "How large should that cushion be — and should it be the same for every partner?"

The answer, as this project demonstrates, is no. Different lending partners carry
different levels of risk, and the holdback percentage should reflect that.

---

## Step 1 — We Started With the Data

We used a dataset of **255,347 real loan records**. Each record described one
borrower: their credit score, income, loan amount, employment status, whether they
had a co-signer, and several other characteristics.

Most importantly, each loan was labelled as either:
- **Default = 0** — the borrower kept paying (225,694 loans, or 88.4%)
- **Default = 1** — the borrower stopped paying (29,653 loans, or 11.6%)

Before we could use this data, we had to clean and prepare it. This is called
**data preprocessing**, and it involved three things:

- **Removing outliers** — a few loans had extreme values (very high income, very
  large loan amounts) that could distort the analysis. We capped these at
  reasonable limits. This is called **winsorization**.

- **Standardizing numbers** — loan amounts and interest rates are measured on very
  different scales. A loan of $50,000 and an interest rate of 8% cannot be directly
  compared in a mathematical model without adjusting them to the same scale.
  We used a technique called **standardization** to fix this.

- **Converting text categories to numbers** — the model cannot read words like
  "Full-time" or "Bachelor's degree." We converted these into a series of 0s and 1s
  so the model could process them. This is called **one-hot encoding**.

We also created two additional pieces of information that the raw data did not include:

- **Lending partner labels** — we assigned each loan to one of five fictional
  lending partners (Partner A through E), so we could measure risk at the
  partner level rather than just across the whole portfolio.

- **Origination dates** — we simulated the date each loan was originally issued,
  spanning January 2015 to December 2024. This allowed us to analyze how loan
  performance changes over time.

---

## Step 2 — We Built a Statistical Model

Once the data was clean, we built a **logistic regression model**. This is one of
the most well-established and trusted tools in credit risk analysis. Banks and
regulators have used it for decades because it is transparent — you can see exactly
which factors it is using and how much weight it gives to each one.

The model reads the characteristics of each loan and produces a single number:
the **Probability of Default (PD)** — a score between 0 and 1 that represents
the likelihood that a given borrower will stop making payments.

For example:
- A PD of 0.08 means the model estimates an 8% chance that borrower will default.
- A PD of 0.45 means there is a 45% chance.

To make sure the model was learning real patterns and not just memorizing the data
it was trained on, we split the dataset into two groups:
- **80% training set** — used to teach the model.
- **20% test set** — held back and used to evaluate the model on loans it had
  never seen before.

This is called a **train-test split**, and it is a standard quality control
procedure in model development.

---

## Step 3 — We Validated the Model

Before trusting the model's output, we needed to measure how good it actually is.

The metric we used is called the **ROC-AUC score** (Area Under the Curve). It
measures how well the model separates borrowers who will default from those who
will not. The score ranges from 0.50 (no better than a coin flip) to 1.00
(perfect prediction).

**Our model scored 0.7531.**

Industry standard for a credit risk model to be considered reliable is a score
above 0.70. Our model clears that threshold comfortably.

We also produced a regulatory-grade statistical summary table showing which
borrower characteristics were the strongest predictors of default, and whether
those findings were statistically reliable (i.e., not due to random chance).
This is the kind of output a risk committee or regulator would review during a
model approval process.

---

## Step 4 — We Translated the Model Into a Dollar Amount

A probability score on its own does not mean much to a finance team. What matters
is: how much money are we at risk of losing?

To answer this, we used the **Expected Loss (EL) formula**, which is the
industry standard used by banks under the Basel II and Basel III regulatory
frameworks:

```
Expected Loss = Probability of Default  x  Exposure at Default  x  Loss Given Default
             =        PD               x          EAD            x        LGD
```

- **PD (Probability of Default)** — from our logistic regression model.
- **EAD (Exposure at Default)** — the outstanding loan balance at the time of
  default. We used the original loan amount as a proxy.
- **LGD (Loss Given Default)** — the percentage of the loan the bank cannot
  recover after a default. We assumed 50%, meaning the bank recovers half the
  value of a defaulted loan. This is a conservative but standard assumption.

We calculated Expected Loss for every single loan in the portfolio — all 255,347
of them.

### Adding the Variance Buffer

Expected Loss tells us what we anticipate losing under normal conditions. But
financial markets are not always normal. A sudden recession, a rise in unemployment,
or a sector-wide shock can push default rates far above expectations.

To account for this, we added a **variance buffer** — an additional reserve
calculated from the statistical spread of losses within each partner's portfolio.
This buffer absorbs **unexpected loss** — the difference between what we planned
for and what actually happens in a stress scenario.

The final holdback recommendation for each lending partner is:

```
Holdback % = (Expected Loss + Variance Buffer) / Total Outstanding Portfolio
```

---

## Step 5 — We Analyzed Performance Over Time

Finally, we conducted a **vintage analysis** (also called a cohort analysis).

A "vintage" in lending refers to all loans that were originated in the same time
period — for example, all loans issued in 2018. By grouping loans this way, we
can ask: did loans from certain years perform worse than others?

This type of analysis is critical for spotting patterns that a single snapshot of
data would miss. For instance, loans originated just before a recession tend to
have higher default rates than loans originated during the recovery that followed.

We tracked default rates across ten years of originations (2015–2024) and broke
the results down by lending partner, producing a visual "heat map" that shows
exactly which partner-vintage combinations carried the highest risk.

---

## Summary

In plain terms, here is what we built:

1. Cleaned and prepared 255,347 loan records for statistical analysis.
2. Built a logistic regression model that assigns a default probability to every loan.
3. Validated the model against a rigorous performance benchmark (ROC-AUC > 0.70).
4. Calculated the expected dollar loss for every loan using the industry-standard
   EL = PD x EAD x LGD formula.
5. Added a buffer for unexpected losses and converted everything into a recommended
   holdback percentage — one number, per lending partner, that the bank can act on.
6. Analyzed ten years of loan performance by origination year to identify which
   vintages and partners carried elevated risk.

The result is a framework that is statistically defensible, fully documented,
and reproducible — meaning any analyst can open the code, run it, and arrive at
the exact same answer. That is what regulators and risk committees require.
