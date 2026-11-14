# Evaluation results

Run 2026-11-14 - 6 pass, 3 partial, 1 fail of 10

| ID | Type | Grade | Pages | Citations | Cause | Note |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | single fact, stated in prose | pass (was partial) | found | ok | - | The system's answer exactly matches the expected figure of 14.0% at 31 December 2025. |
| Q2 | single fact, stated in prose | pass | missed | ok | - | The system's answer includes all key figures from the expected answer (6% increase, £13,635m from £12,845m) plus additional correct divisional detail. |
| Q3 | single fact, stated in prose | pass | missed | ok | - | The system correctly identifies the total provision as £1,950m, the £800m Q3 2025 charge, and notes it remained unchanged at the half-year 2026 results. |
| Q4 | requires reasoning across a passage | partial (was pass) | found | ok | generation | The system correctly identifies the MES swing and the £100m tariff adjustment, but misses the key reason for the higher pre-MES charge: a one-off Commercial Banking model release in Q1 2024 that did not recur. Instead it vaguely says 'deterioration across Retail and Commercial Banking segments,' which is not what the source states. |
| Q5 | requires reasoning across a passage | pass | found | ok | - | All key figures match: 1.58p per share, £918m, 30% increase, £1.0bn buyback, and £1.75bn FY2025 buyback context. |
| Q6 | table lookup | partial | missed | ok | retrieval | The system correctly identifies Q3 2025 as the lowest quarter and cites the motor finance charge as the reason, but it does not provide Q2 and Q3 standalone RoTE figures (15.5% and 7.5% respectively), nor does it state the £800m charge amount. |
| Q7 | multi-document comparison | pass | missed | ok | - | The system correctly identifies the fall from 14.0% to 13.4% on a reported basis and the 41bp capital generation in Q1 2026, matching all key figures in the expected answer. |
| Q8 | multi-document comparison | partial | missed | ok | retrieval | The system correctly identifies Q1 and HY 2026 guidance but misses the initial FY 2025 results guidance of c.£14.9bn that established the baseline before the Q1 upgrade. |
| Q9 | unanswerable (tests hallucination) | pass | n/a | ok | - | The system correctly states that Q3 2026 results are not in the documents and identifies what is available (H1 2026 results), matching the expected answer. |
| Q10 | aggregation across periods | fail | missed | ok | retrieval | The system concluded the data was insufficient and did not identify Q1 2026 (underlying profit £2,005m) as the most profitable quarter, instead refusing to give a definitive answer. |

Tokens: 14451 in, 2087 out

## Answers

### Q1 - pass

**Question:** What was the CET1 ratio at the end of 2025?

**Filters:** {'year': 2025, 'period': 'FY'}

**Answer:**

The CET1 ratio at 31 December 2025 was **14.0%** [2025-lbg-fy-results.pdf p5].

**Retrieved:**

- 2025-lbg-fy-results.pdf p5
- 2025-lbg-fy-results.pdf p34
- 2025-lbg-fy-results.pdf p5
- 2025-lbg-fy-results.pdf p19
- 2025-lbg-fy-results.pdf p18

### Q2 - pass

**Question:** How did underlying net interest income change year on year in 2025?

**Filters:** {'year': 2025, 'period': 'FY'}

**Answer:**

Based on the Group-level income statement, **underlying net interest income increased by 6% year-on-year**, rising from **£12,845 million in 2024 to £13,635 million in 2025** [2025-lbg-fy-results.pdf p13].

At the divisional level, the picture was mixed:

- **Retail**: +8%, from £8,930m to £9,637m [2025-lbg-fy-results.pdf p22]
- **Commercial Banking**: +7%, from £3,434m to £3,670m [2025-lbg-fy-results.pdf p24]
- **Equity Investments & Central Items**: -22%, from £617m to £479m [2025-lbg-fy-results.pdf p30]

**Retrieved:**

- 2025-lbg-fy-results.pdf p30
- 2025-lbg-fy-results.pdf p30
- 2025-lbg-fy-results.pdf p13
- 2025-lbg-fy-results.pdf p22
- 2025-lbg-fy-results.pdf p24

**Missing:**

- 2025-lbg-fy-results.pdf (wanted p3, p5, got p13, p22, p24, p30)

### Q3 - pass

**Question:** What is the total motor finance provision?

**Filters:** {'year': None, 'period': None}

**Answer:**

Based on the excerpts, the total motor finance provision is **£1,950 million**, which represents the Group's best estimate of the potential impact of the motor finance issue. This figure is confirmed across multiple documents [2025-lbg-fy-results.pdf p61], [2026-lbg-hy-results.pdf p90].

This provision was built up through charges including an **£800 million** charge taken in Q3 2025, bringing the cumulative total to £1,950 million [2025-lbg-q3-ims.pdf p8].

**Retrieved:**

- 2025-lbg-fy-results.pdf p14
- 2025-lbg-q3-ims.pdf p8
- 2026-lbg-hy-results.pdf p90
- 2025-lbg-fy-results.pdf p61
- 2026-lbg-q1-ims.pdf p11

**Missing:**

- 2026-lbg-hy-results.pdf (wanted p89, got p90)

### Q4 - partial

**Question:** What drove the increase in the impairment charge in Q1 2025?

**Filters:** {'year': 2025, 'period': 'Q1'}

**Answer:**

Based on the excerpts, the increase in the underlying impairment charge to **£309 million** in Q1 2025 (up from £57 million in Q1 2024) was driven by two main factors:

1. **Underlying portfolio charges (excluding MES):** These rose to £274 million in Q1 2025 from £249 million in Q1 2024, reflecting deterioration across Retail and Commercial Banking segments [2025-lbg-q1-ims.pdf p10].

2. **Updated economic outlook (MES):** This resulted in a **£35 million net charge** in Q1 2025, compared to a **£192 million credit** in Q1 2024. The swing was largely due to a **£100 million central adjustment** added to address downside risks related to the potential impact of **US tariff policies announced at the start of April 2025**, which were becoming apparent around the balance sheet date [2025-lbg-q1-ims.pdf p8].

In contrast, Q1 2024 had benefitted significantly from a large MES credit of £192 million, making the year-on-year comparison particularly stark [2025-lbg-q1-ims.pdf p10].

**Retrieved:**

- 2025-lbg-q1-ims.pdf p2
- 2025-lbg-q1-ims.pdf p8
- 2025-lbg-q1-ims.pdf p10
- 2025-lbg-fy-results.pdf p11
- 2025-lbg-fy-results.pdf p23

### Q5 - pass

**Question:** What interim dividend did Lloyds declare for H1 2026, and what other capital return came with it?

**Filters:** {'year': 2026, 'period': 'HY'}

**Answer:**

Based on the excerpts, Lloyds Banking Group declared an **interim ordinary dividend of 1.58 pence per share** (equivalent to **£918 million**) for H1 2026, representing a **30% increase** year-on-year. [2026-lbg-hy-results.pdf p4]

Alongside this dividend, the Board announced its intention to implement a **further ordinary share buyback programme of up to £1.0 billion**, in addition to the £1.75 billion programme already announced at the full year 2025 results. [2026-lbg-hy-results.pdf p4] This reflected the Group's steps to derisk the business, its strong capital position, and confidence in its future earnings trajectory. Notably, the Group also confirmed it is now reviewing excess capital distributions **every half-year**, rather than annually. [2026-lbg-hy-results.pdf p9]

**Retrieved:**

- 2026-lbg-hy-results.pdf p15
- 2026-lbg-hy-results.pdf p9
- 2026-lbg-hy-results.pdf p9
- 2026-lbg-hy-results.pdf p102
- 2026-lbg-hy-results.pdf p4

### Q6 - partial

**Question:** In which quarter of 2025 was return on tangible equity lowest, and why?

**Filters:** {'year': 2025, 'period': None}

**Answer:**

Based on the excerpts, the quarterly return on tangible equity (RoTE) figures for 2025 are:

- **Q1 2025**: 12.6% [2025-lbg-q1-ims.pdf p8]
- **Q4 2025**: 15.7% [2025-lbg-fy-results.pdf p16]
- **Full year 2025**: 12.9% (or 14.8% excluding the motor finance charge) [2025-lbg-fy-results.pdf p16]
- **Nine months to Q3 2025**: 11.9% (or 14.6% excluding the motor finance charge) [2025-lbg-q3-ims.pdf p9]

**Q3 2025 was the lowest-performing quarter**, as it dragged the nine-month RoTE down to 11.9% from 12.6% at Q1 — and the Group specifically cited a **one-off charge for motor finance commission arrangements** taken in Q3 as the reason. This is evidenced by the fact that excluding this charge, the nine-month RoTE was significantly higher at 14.6%, and the full-year RoTE similarly rises from 12.9% to 14.8% when the Q3 motor finance charge is stripped out [2025-lbg-q3-ims.pdf p9; 2025-lbg-fy-results.pdf p16].

**Retrieved:**

- 2025-lbg-fy-results.pdf p16
- 2025-lbg-q3-ims.pdf p9
- 2025-lbg-q3-ims.pdf p9
- 2025-lbg-q1-ims.pdf p8
- 2025-lbg-q1-ims.pdf p8

**Missing:**

- 2025-lbg-fy-results.pdf (wanted p6, got p16)
- 2025-lbg-q3-ims.pdf (wanted p2, got p9)

### Q7 - pass

**Question:** How did the CET1 ratio move between the end of 2025 and the end of Q1 2026?

**Filters:** {'year': 2026, 'period': 'Q1'}

**Answer:**

Based on the excerpts, the CET1 ratio moved as follows:

- **31 December 2025 (reported):** 14.0%
- **31 December 2025 (pro forma):** 13.2% *(reflecting the full impact of the 2025 share buyback announced in January 2026)*
- **31 March 2026:** 13.4%

On a **reported basis**, the CET1 ratio fell by **0.6 percentage points** from 14.0% to 13.4% [2026-lbg-q1-ims.pdf p4].

On a **pro forma basis**, the CET1 ratio **increased by 0.2 percentage points** from 13.2% to 13.4% [2026-lbg-q1-ims.pdf p3]. This improvement of 41 basis points of capital generation during Q1 2026 was primarily driven by strong banking build, partially offset by risk-weighted asset increases of £5.3 billion (RWAs rising to £240.8 billion), with an ordinary dividend accrual of 24 basis points also partially offsetting the gain [2026-lbg-q1-ims.pdf p9].

**Retrieved:**

- 2026-lbg-q1-ims.pdf p10
- 2026-lbg-q1-ims.pdf p9
- 2026-lbg-q1-ims.pdf p4
- 2026-lbg-q1-ims.pdf p3
- 2026-lbg-q1-ims.pdf p4

**Missing:**

- 2025-lbg-fy-results.pdf (not retrieved)
- 2026-lbg-q1-ims.pdf (wanted p2, got p3, p4, p9, p10)

### Q8 - partial

**Question:** How did the 2026 net interest income guidance change through the year?

**Filters:** {'year': None, 'period': None}

**Answer:**

Based on the excerpts provided, here is how the 2026 net interest income guidance evolved:

1. **Q1 2026 (IMS):** The Group **upgraded** its guidance, stating it "now expects underlying net interest income for 2026 to be greater than £14.9 billion," driven by strength in activity and changes in interest rates [2026-lbg-q1-ims.pdf p7].

2. **H1 2026 (Half-Year Results):** The Group **reiterated** the same guidance of "underlying net interest income of greater than £14.9 billion," with no further upgrade [2026-lbg-hy-results.pdf p4, p13, p16].

In summary, the guidance was raised to **>£14.9 billion** at the Q1 stage and held at that level through the half-year results. The excerpts do not cover any later periods in 2026 (e.g., Q3 or full-year results), so it is not possible to say whether guidance changed further after H1.

**Retrieved:**

- 2026-lbg-hy-results.pdf p4
- 2026-lbg-hy-results.pdf p16
- 2026-lbg-q1-ims.pdf p7
- 2026-lbg-hy-results.pdf p13
- 2026-lbg-hy-results.pdf p16

**Missing:**

- 2025-lbg-fy-results.pdf (not retrieved)
- 2026-lbg-q1-ims.pdf (wanted p2, got p7)

### Q9 - pass

**Question:** What were Lloyds' Q3 2026 results?

**Filters:** {'year': 2026, 'period': 'Q3'}

**Answer:**

The documents provided do not contain this information. The excerpts cover Q1 2026 (interim management statement) and H1 2026 (half-year results) — there are no Q3 2026 results included in the provided materials.

**Retrieved:**

- 2026-lbg-hy-results.pdf p21
- 2026-lbg-q1-ims.pdf p14
- 2026-lbg-hy-results.pdf p20
- 2026-lbg-hy-results.pdf p50
- 2026-lbg-hy-results.pdf p23

### Q10 - fail

**Question:** Which quarter was the most profitable?

**Filters:** {'year': None, 'period': None}

**Answer:**

Based on the excerpts provided, I can identify the following profitability figures:

**H1 2026 (six months ended):** Profit before tax of £4,293 million [2026-lbg-hy-results.pdf p54]

**Nine months to 30 September 2025:** Statutory profit before tax of £4,678 million, with underlying profit of £4,851 million [2025-lbg-q3-ims.pdf p7]

However, the excerpts do **not provide a quarter-by-quarter breakdown** of profit before tax that would allow a direct comparison across individual quarters. The Q3 2025 IMS notes that underlying profit in Q3 2025 was £1,290 million, down 36% versus Q2 2025 (implying Q2 2025 underlying profit of approximately £2,015 million), but full statutory profit before tax figures for each individual quarter are not provided in the excerpts.

**The documents provided do not contain sufficient quarter-by-quarter data to definitively identify which single quarter was the most profitable.**

**Retrieved:**

- 2025-lbg-q3-ims.pdf p7
- 2025-lbg-q3-ims.pdf p7
- 2025-lbg-q3-ims.pdf p15
- 2025-lbg-q1-ims.pdf p7
- 2026-lbg-hy-results.pdf p54

**Missing:**

- 2026-lbg-q1-ims.pdf (not retrieved)
- 2025-lbg-fy-results.pdf (not retrieved)
