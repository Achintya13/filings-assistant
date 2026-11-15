# Evaluation results

Run 2026-11-15 - 6 pass, 3 partial, 1 fail of 10

| ID | Type | Grade | Pages | Citations | Cause | Note |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | single fact, stated in prose | pass | found | ok | - | The system's answer matches the expected answer exactly, providing 14.0% at 31 December 2025. |
| Q2 | single fact, stated in prose | pass | missed | ok | - | The system's answer matches all key points of the expected answer exactly. |
| Q3 | single fact, stated in prose | pass | missed | ok | - | The system's answer matches all key points of the expected answer. |
| Q4 | requires reasoning across a passage | partial | found | ok | generation | The system mentions higher ex-MES charge but attributes it to increases across Retail and Commercial Banking rather than specifically to a one-off Commercial Banking model release in Q1 2024 not recurring. |
| Q5 | requires reasoning across a passage | pass | found | ok | - | The system's answer matches all key points of the expected answer exactly. |
| Q6 | table lookup | partial | missed | ok | retrieval | The system correctly identifies Q3 as lowest and mentions the motor finance charge as the reason, but does not provide the specific Q3 standalone RoTE of 7.5%, Q2 figure of 15.5%, or the specific £800m charge amount. |
| Q7 | multi-document comparison | pass | missed | ok | - | The system's answer confirms both key points: the fall from 14.0% to 13.4% and capital generation of 41bp. |
| Q8 | multi-document comparison | partial | missed | ok | retrieval | The system correctly identifies the Q1 upgrade and HY reiteration but fails to include the starting FY2025 guidance of c.£14.9bn, claiming it lacks that information. |
| Q9 | unanswerable (tests hallucination) | pass | n/a | ok | - | The system correctly states the documents do not contain Q3 2026 results and identifies what is available (H1 2026), matching the expected answer. |
| Q10 | aggregation across periods | fail | missed | ok | retrieval | The system's answer does not identify Q1 2026 as the most profitable quarter and instead states it cannot determine which quarter was most profitable, while also citing an incorrect Q3 2025 underlying profit figure of £1,290m rather than providing the correct figures. |

Tokens: 14741 in, 1925 out

## Answers

### Q1 - pass

**Question:** What was the CET1 ratio at the end of 2025?

**Filters:** {'year': 2025, 'period': 'FY'}

**Answer:**

The CET1 ratio at 31 December 2025 was **14.0%** (compared to 14.2% at 31 December 2024). [2025-lbg-fy-results.pdf p5]

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

Based on the excerpts, Group underlying net interest income increased by **6%** to **£13,635 million** in 2025, up from **£12,845 million** in 2024 [2025-lbg-fy-results.pdf p13].

At a divisional level:
- **Retail**: increased 8% to £9,637m (2024: £8,930m) [2025-lbg-fy-results.pdf p22]
- **Commercial Banking**: increased 7% to £3,670m (2024: £3,434m) [2025-lbg-fy-results.pdf p24]
- **Equity Investments and Central Items**: decreased 22% to £479m (2024: £617m) [2025-lbg-fy-results.pdf p30]

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

Based on the excerpts, the total motor finance provision is **£1,950 million**, which represents the Group's best estimate of the potential impact of the motor finance issue. This figure is consistent across multiple documents:

- [2025-lbg-fy-results.pdf p14]
- [2025-lbg-fy-results.pdf p61]
- [2026-lbg-hy-results.pdf p90]

The provision reached this level after an £800 million charge was taken in Q3 2025, bringing the cumulative total to £1,950 million [2025-lbg-q3-ims.pdf p8].

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

Based on the excerpts, the increase in the underlying impairment charge to **£309 million** in Q1 2025 (versus £57 million in Q1 2024) was driven by two main factors:

1. **Higher underlying impairment** (excluding economic outlook updates): The charge ex-MES was £274 million in Q1 2025 versus £249 million in Q1 2024, reflecting increases across Retail and Commercial Banking. [2025-lbg-q1-ims.pdf p10]

2. **Updated multiple economic scenarios (MES)**: This resulted in a **£35 million net charge** in Q1 2025, compared to a **£192 million credit** in Q1 2024. Within this, a **£100 million central adjustment** was included to address downside risks related to the potential impact of **US tariff policies announced at the start of April 2025**, which were becoming apparent around the balance sheet date. [2025-lbg-q1-ims.pdf p8]

The swing in the MES component — from a large credit of £192 million in Q1 2024 to a net charge of £35 million in Q1 2025 — was therefore a significant driver of the year-on-year increase.

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

Alongside this dividend, the Board announced its intention to implement a **further ordinary share buyback programme of up to £1.0 billion**, in addition to the £1.75 billion buyback programme that had already been announced at the full year 2025 results. [2026-lbg-hy-results.pdf p4]

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

Based on the excerpts, the quarterly return on tangible equity figures for 2025 are:

- **Q1 2025**: 12.6% [2025-lbg-q1-ims.pdf p8]
- **Q3 2025 (nine months cumulative)**: 11.9%, or 14.6% excluding the motor finance charge [2025-lbg-q3-ims.pdf p9]
- **Q4 2025**: 15.7% [2025-lbg-fy-results.pdf p16]
- **Full year 2025**: 12.9%, or 14.8% excluding the motor finance charge [2025-lbg-fy-results.pdf p16]

The excerpts do not provide standalone quarterly RoTE figures for Q2 and Q3 individually, only cumulative figures. However, the dragging down of the nine-month cumulative RoTE to 11.9% (versus 12.6% after Q1) points to **Q3 2025** as the weakest quarter, and the excerpts explicitly attribute this to the **third quarter charge for motor finance commission arrangements** [2025-lbg-q3-ims.pdf p9].

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

On a **pro forma basis**, the CET1 ratio **increased by 0.2 percentage points** (from 13.2% to 13.4%), driven by capital generation of 41 basis points — primarily from strong banking build — partially offset by risk-weighted asset increases of 31 basis points and an ordinary dividend accrual of 24 basis points. [2026-lbg-q1-ims.pdf p9, p10]

On a **reported basis**, the ratio **fell by 0.6 percentage points** (from 14.0% to 13.4%), as the December 2025 reported figure had not yet reflected the share buyback. [2026-lbg-q1-ims.pdf p4]

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

- **Q1 2026 (IMS):** The Group **upgraded** its guidance, stating it "now expects underlying net interest income for 2026 to be greater than £14.9 billion," driven by strength in activity and changes in interest rates [2026-lbg-q1-ims.pdf p7].

- **H1 2026 (Half-Year Results):** The Group **reiterated** its guidance of underlying net interest income of greater than £14.9 billion, unchanged from the Q1 upgrade [2026-lbg-hy-results.pdf p4, p13, p16].

The excerpts do not contain the original guidance figure set at the start of 2026 (i.e., from the full-year 2025 results), so it is not possible to determine from these documents alone what the guidance was before the Q1 upgrade.

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

The documents provided do not contain this information. The excerpts cover Q1 2026 (ending 31 March 2026) and H1 2026 (ending 30 June 2026), but do not include any Q3 2026 results.

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

Based on the excerpts provided, I can identify the following quarterly profit figures:

- **Q1 2025**: Underlying profit implied from the Q1 IMS, with net income of £4,391 million for the quarter [2025-lbg-q1-ims.pdf p7]
- **Q3 2025**: Underlying profit of £1,290 million [2025-lbg-q3-ims.pdf p7]
- **H1 2026**: Profit before tax of £4,293 million for the half-year period [2026-lbg-hy-results.pdf p54]

However, the excerpts do not provide a consistent, comparable quarterly statutory profit before tax figure across all quarters that would allow a definitive ranking of which single quarter was most profitable. The documents provided do not contain sufficient information to answer this question comprehensively.

**Retrieved:**

- 2025-lbg-q3-ims.pdf p7
- 2025-lbg-q3-ims.pdf p7
- 2025-lbg-q3-ims.pdf p15
- 2025-lbg-q1-ims.pdf p7
- 2026-lbg-hy-results.pdf p54

**Missing:**

- 2026-lbg-q1-ims.pdf (not retrieved)
- 2025-lbg-fy-results.pdf (not retrieved)
