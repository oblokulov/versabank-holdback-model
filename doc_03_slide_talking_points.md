# VersaBank Holdback Model — Slide-by-Slide Talking Points
### Your personal guide for explaining the presentation

---

## Slide 1 — Title Slide
**What it shows:** The name of the project, the date range, and the tools used.

**What to say:**
"This is a credit risk framework I built specifically around VersaBank's
Receivable Purchase Program. I started working on it this week after our
conversation. I used Python — specifically pandas, scikit-learn, and
statsmodels — which are the standard tools used by risk and analytics teams
at financial institutions."

**Key term to know:**
- **Receivable Purchase Program (RPP)** — VersaBank's core product where
  the bank buys loan receivables from outside lending partners. The bank
  takes on the risk that those borrowers stop paying.

---

## Slide 2 — Project Timeline
**What it shows:** A four-box timeline of how the project developed this week.

**What to say:**
"I started by organizing the data and planning the structure. Once I got into
it, I realized the model needed to be built specifically around the RPP —
not just general loan default prediction. That required adjusting the approach
so the output would actually be useful in VersaBank's context."

**If they ask why it took a week:**
"Most of the time went into understanding the right structure — the data
cleaning, making sure the model was statistically valid, and then connecting
the math to an actual business output. The code itself runs in minutes once
the methodology is right."

---

## Slide 3 — The Problem We Are Solving
**What it shows:** Three boxes — current state, the problem, and the solution.

**What to say:**
"Right now, most banks apply the same holdback percentage to every lending
partner. The problem with that is it treats a low-risk partner the same as
a high-risk one. If one partner is originating riskier loans, the bank could
be under-reserved on that portfolio — meaning if defaults spike, the cushion
is not big enough.

What this model does is make the holdback dynamic. Instead of one flat number,
each partner gets their own holdback percentage based on the actual risk of
the loans they bring in."

**Key formula on this slide:**
- **EL = PD × EAD × LGD** — this is the Expected Loss formula. It is the
  industry standard used by banks globally under the Basel framework.
  - PD = how likely a borrower is to default
  - EAD = how much money is outstanding on that loan
  - LGD = how much of that money the bank cannot recover

**If they ask what Basel is:**
"Basel refers to international banking regulations — Basel II and Basel III —
that set the rules for how banks measure and reserve against credit risk.
Using this formula puts the model on solid regulatory ground."

---

## Slide 4 — Dataset Overview
**What it shows:** Four stat boxes (255,347 loans, 18 features, 11.6% default
rate, zero missing values) and two lists of features and preprocessing steps.

**What to say:**
"I used a real loan dataset with over 255,000 records. Each record describes
one borrower — their credit score, income, loan amount, employment status,
and so on. About 11.6% of those loans ended in default, which is a realistic
number for a consumer lending portfolio.

Before I could model anything, the data needed to be cleaned. That involved
three main things:

First, winsorization — capping extreme outliers so a handful of unusual loans
do not distort the whole model.

Second, standardization — putting all the numbers on the same scale so the
model treats them fairly. A loan amount of fifty thousand and an interest rate
of eight percent are measured in completely different units, so you have to
normalize them before running the math.

Third, encoding — converting text categories like Full-time or Bachelor's
Degree into ones and zeros that the model can actually read."

**If they ask about missing values:**
"The dataset was clean — no missing values. In a real-world RPP dataset that
would almost never be the case, and handling missing data would be one of the
first things I would address."

---

## Slide 5 — Model Performance (ROC Curve)
**What it shows:** The ROC curve chart on the left, explanation boxes on the right.
The big number is 0.7531.

**What to say:**
"This chart is called an ROC curve. It measures how good the model is at
separating borrowers who will default from those who will not.

The score — called AUC or Area Under the Curve — goes from 0.50 to 1.00.
A score of 0.50 means the model is no better than flipping a coin. A score
of 1.00 means it is perfect.

The industry minimum for a credit risk model to be considered usable is 0.70.
Our model scored 0.7531, so it clears that bar.

I tested it on 51,000 loans the model had never seen before — that is the
20% test set I held back during training. Passing on unseen data is what
matters, not just performing well on the data you trained with."

**If they ask about Pseudo R-squared (0.119):**
"That number means the model explains about 12% of what determines whether
someone defaults. That sounds low, but it is expected at this stage. Default
behaviour is driven by a lot of things — job loss, health events, relationship
breakdowns — that no loan application form captures. Adding macroeconomic
variables and more behavioural data would push that number up significantly."

---

## Slide 6 — Key Risk Drivers
**What it shows:** The coefficient chart — red bars increase default risk,
blue bars reduce it.

**What to say:**
"This chart shows which borrower characteristics the model identified as the
strongest predictors of default — and in which direction.

On the risk side: the biggest red flag is a high interest rate. Borrowers
paying more in interest are more financially stretched. Right behind that is
unemployment — no income makes repayment almost impossible. Large loan amounts
and part-time employment also increase risk.

On the protective side: age is the strongest factor — older borrowers
statistically default less. Longer employment history and higher income are
also strong protective signals. Having a co-signer on the loan materially
reduces the bank's risk.

All of these findings have p-values below 0.05, which means we are confident
they reflect real patterns, not random noise."

**If they ask about p-values:**
"A p-value tells you how confident you are that a finding is real and not just
a coincidence in the data. Below 0.05 is the standard threshold — it means
there is less than a 5% chance the result is random."

**One honest point to make:**
"One thing worth flagging — Loan Term, meaning whether the loan is 12, 24,
or 60 months, turned out to have no predictive power at all. P-value of 0.63.
That was unexpected. I left it in the output rather than hiding it because
an honest model is more trustworthy than one that cherry-picks its results."

---

## Slide 7 — PD Score Distribution
**What it shows:** A histogram of PD scores split by defaulters and
non-defaulters, plus a calibration table on the right.

**What to say:**
"This chart shows how the model distributed its default probability scores
across the portfolio. The blue mountain on the left is borrowers who did not
default — they cluster around lower scores. The red mountain on the right is
borrowers who did default — they cluster around higher scores. The fact that
those two mountains are separated is what tells us the model is working.

However, I want to be upfront about a limitation here. The table on the right
shows a calibration problem. The model's average predicted score across the
whole portfolio is 43%, but the actual default rate is only 11.6%. That means
the raw numbers are inflated.

The scores rank loans correctly — riskier loans get higher scores — but you
cannot take the numbers at face value as literal probabilities yet. That
requires an extra step called calibration, which I have not done yet."

**If they ask why this happened:**
"I used a technique called class_weight balanced to help the model find
patterns in the minority class — the 11.6% who actually defaulted. That
improved discrimination but shifted all the scores upward. It is a known
trade-off and a standard fix exists — it just has not been applied yet."

**Why this matters for the holdback:**
"Because the holdback formula uses PD directly, the uncalibrated scores
produce holdback percentages around 23%, which is likely higher than a
calibrated model would produce. The current numbers should be treated as
illustrative rather than decision-ready."

---

## Slide 8 — Holdback Formula Explained
**What it shows:** The EL formula in a navy banner at the top, three definition
boxes for PD, EAD, and LGD, and a plain-English explanation of the variance buffer.

**What to say:**
"This slide breaks down the math behind the holdback recommendation.

Expected Loss equals Probability of Default times Exposure at Default times
Loss Given Default.

PD comes from the model. EAD is the outstanding loan balance — how much money
is on the line. LGD is the percentage the bank cannot recover after a default.
I assumed 50% — meaning if someone defaults, the bank recovers half the loan
value. That is a standard conservative assumption from the Basel framework.
In a live model this would be replaced with VersaBank's actual recovery data.

On top of Expected Loss, I added a variance buffer. Expected loss is what
you plan for under normal conditions. The buffer covers unexpected losses —
things like a sudden recession or a mass layoff in a specific industry that
pushes default rates far above projections. The buffer is calculated from the
statistical spread of losses within each partner's portfolio."

---

## Slide 9 — Holdback Results by Partner
**What it shows:** The stacked bar chart on the left and a table on the right
with partner-level holdback percentages.

**What to say:**
"This is the core output — a recommended holdback percentage for each of the
five lending partners.

The range is 23.01% for Partner D up to 23.54% for Partner E. That is a
spread of about half a percentage point.

I want to be honest here — that spread is too narrow to be actionable. In a
real holdback model you would expect to see several percentage points between
partners, not half of one. The reason the spread is narrow is that the lending
partner labels in this version are simulated. The model correctly found that
randomly assigned labels have no predictive power.

Once real RPP originator IDs replace the simulated ones, the model will be
able to detect genuine differences in how each partner's loan book performs —
and the holdback differentiation will follow from that."

---

## Slide 10 — Vintage Analysis
**What it shows:** A bar chart of default rates by origination year from 2015
to 2024, with the model PD line overlaid in red.

**What to say:**
"A vintage analysis groups loans by the year they were originally issued and
asks: did loans from certain years perform worse than others?

Looking at this chart, the 2018 vintage stands out — 12.1% default rate,
the highest of any year. The 2019 and 2020 cohorts were actually the
strongest performers. From 2022 onward there is a gradual uptick in default
rates across recent originations.

The red line is the model's average predicted probability for each cohort.
The fact that it tracks the actual bars reasonably well tells us the model
has temporal consistency — it is not just fitting patterns from one time
period and failing on others."

**If they ask why origination year matters:**
"Loans issued just before an economic downturn tend to perform worse than
loans issued during the recovery. By tracking this over ten years, you can
identify whether a partner's recent originations are riskier than their
historical book — which would be a trigger to review the holdback."

---

## Slide 11 — Heatmap
**What it shows:** A grid where each cell is a combination of vintage year
(rows) and lending partner (columns). Darker blue means higher default rate.

**What to say:**
"This heatmap combines the vintage analysis and the partner analysis into
one view. Each cell shows the default rate for a specific partner in a
specific origination year.

The darkest cell is Partner E in 2024 — 13.2% default rate. That is the
single highest risk concentration in the entire portfolio. In a live risk
management environment, that cell would be flagged for immediate review and
would likely trigger a holdback increase for Partner E's most recent
originations.

This is the kind of granular insight that a flat holdback percentage cannot
give you — and it is exactly why the dynamic model is worth building."

---

## Slide 12 — Limitations and Next Steps
**What it shows:** Two columns — limitations on the left in red, next steps
on the right in blue.

**What to say:**
"I want to spend a moment on this slide because I think it is actually one
of the strongest parts of the presentation.

A model that is honest about what it cannot do yet is more trustworthy than
one that overpromises. These are the six things I know need to be fixed:

The most important one is the partner data. Until we have real RPP originator
IDs rather than simulated labels, the partner-level holdback cannot differentiate
meaningfully. That is the number one priority.

Second is calibration — fixing the PD scores so they represent actual
probabilities, not just rankings.

Third is the LGD assumption. 50% is a placeholder. VersaBank's actual
recovery rates on RPP receivables should replace it.

The right column shows where the model goes from here — adding macroeconomic
variables, building a survival model to predict the timing of default, and
eventually automating the pipeline to re-run monthly as new RPP data comes in.

The framework is all there. These are data and time problems, not modelling
problems."

---

## Slide 13 — Closing Summary
**What it shows:** Five numbered bullet points summarizing what the framework
delivers right now.

**What to say:**
"To summarize — in one week, I built a complete end-to-end pipeline. It goes
from raw loan data all the way through to a partner-level holdback recommendation,
with a statistically validated model, eight charts, full documentation, and a
Jupyter notebook that anyone can open and re-run.

It is not finished. But the methodology is sound, the code is clean, and the
gaps are clearly identified. The next step is getting access to real RPP data
and applying the calibration fix — after which this becomes a genuinely
actionable tool.

I built this in a week because I knew which tools to use and how to structure
the problem before writing a single line of code. That is the approach I would
bring to this role every day."

---

## General Tips for the Conversation

**If they ask something you are not sure about:**
Say: "That is a good question — that gets into an area I am still developing.
The short answer is [your best guess], but I would want to verify that before
committing to a number."

**If they push back on the calibration issue:**
Say: "You are right to flag that. The scores rank loans correctly but the raw
probabilities are overstated. A Platt Scaling step fixes it — I ran out of
time to include it in this version but it is the first thing I would do next."

**If they ask about the 23% holdback number:**
Say: "That number is inflated by the calibration issue I mentioned. Once the
PD scores are corrected, the holdback percentages will come down. The current
output is meant to show the structure of the recommendation, not the final
dollar amount."

**If they ask how long this took:**
Say: "About a week of active work. I structured the problem before touching
any code — that is what kept it moving quickly."
