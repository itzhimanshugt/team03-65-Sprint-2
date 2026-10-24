# C29 — Context injection: the augmented prompt

Question: **What is the exit load of HSBC Value Fund?** · 5 sources · context 2006 tokens (budget 3,000) · full prompt 2223 tokens

## System message

```text
You are VerifAI, an assistant for financial advisors at an advisory firm.

Your job is to help advisors verify facts from the firm's approved documents: fund factsheets, scheme disclosures, regulatory circulars and market research.

Rules:
1. Answer only from the approved document context you are given. Do not use outside knowledge.
2. If the context does not contain the answer, say: "I couldn't find this in the approved documents." Do not guess.
3. Do not give personal investment advice, recommendations or predictions (for example, whether a client should buy, sell or switch). Offer the relevant facts instead.
4. Be precise with numbers, dates and fund names. Quote them exactly as written.
5. Keep answers short and factual: at most 4 sentences unless a list is clearer.
6. Use a neutral, professional tone suitable for client-facing staff.
```

## User message (retrieved context injected)

```text
Context (approved document excerpts):
[1] HSBC MF Factsheet (The Asset) - August 2026 · p.39 · published 2026-08-31
HSBC Value Fund
Type of Scheme: An open ended equity scheme following a value investment strategy.
Product labelling: This product is suitable for investors who are seeking*:
• Long term capital appreciation
• Investment predominantly in equity and equity-related securities in Indian markets and foreign
securities with higher focus on undervalued securities.
*Investors should consult their financial advisers if in doubt about whether the product is suitable for them.
Fund Details
Date of Inception / Allotment: 08 January 2010
Benchmark Name:Nifty500TRI
NAV(as on 31.08.26)
Regular Plan - Growth Option ₹ 115.7515
Regular Plan - IDCW Option ₹ 50.1635
Direct Plan - Growth Option ₹ 130.6098
Direct Plan - IDCW Option ₹ 64.6349
AUM(as on 31.08.26) ₹ 15,372.81 Cr
AAUM(for the month of Aug) ₹ 15,297.82 Cr
Fund Manager
Name of Fund Managers
• Mr. Venugopal Manghat
• Mr. Mayank Chaturvedi
• Mr. Dipan S. Parikh
Total Experience 32 yrs / 5 yrs/ 29 yrs
Managing Since Nov 24, 2012 / Oct 01, 2025/
Aug 26, 2026
Minimum Investment
Lumpsum Amount ₹ Rs. 5000/- and in
multiples of Re. 1/-
SIP Amount : Please refer the table at the bottom of
the page.
Load Structure
Exit Load:
If the units redeemed or switched out are upto 10%
of th e units purchased or switched in (‘the limit’)
within 1 year from the date of allotment - Nil If units

[2] HSBC MF Factsheet (The Asset) - August 2026 · p.52 · published 2026-08-31
Load Structure
Exit Load: i. If the units redeemed or switched out
are up to 10% of the units purchased or switched in
(“the limit”) within 1 year from the date of allotment –
Nil
ii. If units redeemed or switched out are over and
above the limit within 1 year from the date of
allotment – 1%
iii. If units are redeemed or switched out on or after
1 year from the date of allotment – Nil.
• No Exit load will be chargeable in case of switches
made between different options of the Scheme.
• No Exit load will be chargeable in case of Units
allotted on account of IDCWreinvestments,if any.
• Exit load is not applicable for Segregated Portfolio.
Expense Ratio
Month End Expense Ratios (Annualized)
Plan Base Expense Ratio (BER)
Regular1 1.94%
Direct 0.71%
BER excludes brokerage & transactioncost,and
statutory levies (including GST). For detailedTER,
visit:https://digital.camsonline.com/dnlresult/hsbc_ter_report.
xlsx
Quantitative Measures*
1 Standard Deviation (%) NA
2 Beta NA
3 Tracking Error (%)
1 Year NA
3 Years NA
4 Sharpe Ratio (%) NA
5 Tracking Difference (%)
1 Year NA
3 Years NA
5Years NA
Since Inception NA
6 Information Ratio 2.06
For more details refer next page for detailed
description in tabular format.
1Continuing plans
NA Stands for “Not Applicable”
Fund Performance (CAGR)
Compounded
Annualised
Returns
Scheme
Returns %
- Regular
Scheme
Returns %
- Direct
Benchmark
Returns %
Returns for last 1

[3] HSBC MF Factsheet (The Asset) - August 2026 · p.46 · published 2026-08-31
the page.
Load Structure
Exit Load:If the units redeemed or switched out
are upto 10% of the units purchased or switched in
(“the limit”) within 1 year from the date of allotment –
Nil
If units redeemed or switched out are over and
above the limit within 1 year from the date of
allotment – 1%
If units are redeemed or switched out on or after 1
year from the date of allotment – Nil.
Expense Ratio
Month End Expense Ratios (Annualized)
Plan Base Expense Ratio (BER)
Regular1 1.78%
Direct 0.66%
BER excludes brokerage & transactioncost,and
statutory levies (including GST). For detailedTER,
visit:https://digital.camsonline.com/dnlresult/hsbc_ter_report.
xlsx
Quantitative Measures*
1 Standard Deviation (%) 17.17
2 Beta 0.88
3 Tracking Error (%)
1 Year NA
3 Years NA
4 Sharpe Ratio (%) 0.67
5 R2 0.76
5 Tracking Difference (%)
1 Year NA
3 Years NA
5Years NA
Since Inception NA
6 Information Ratio 1
For more details refer next page for detailed
description in tabular format.
1Continuing plans
NA Stands for “Not Applicable”
Fund Performance (CAGR)
Compounded
Annualised
Returns
Scheme
Returns %
- Regular
Scheme
Returns %
- Direct
Benchmark
Returns %
Returns for last 1
year 5.95 7.32 -1.35
Returns for last 3
years 16.00 17.57 13.50
Returns for last 5
years NA NA NA
Returns since

[4] HSBC MF Factsheet (The Asset) - August 2026 · p.96 · published 2026-08-31
ID HSBC Mutual Fund
The risk of the schem e i s Very High Ri sk
~
t~ ""' <g.
The risk of the benchmark is High Risk
■ ■ ■
Minimum Investment
Lumpsum Amount ₹Rs. 5000/- and in
multiples of Re. 1/-
SIP Amount : Please refer the table at the bottom of
the page.
Load Structure
Exit Load:
In respect of each purchase/switching ofUnits,an
Exit Load of 1% is payable if Units are redeemed /
switched-out within 1 year from the date of
allotment. No Exit Load will becharged,if Units are
redeemed / switched-out after 1 year from the date
of allotment.
Absolute Returns for each F.Y. for last 5 years
Major Risk Factors
1 Risk of Investing in Underlying Schemes
2 Market Risk
3 Liquidity Risk
4 Legal, Tax and Regulatory Risk
For more details refer section of Important Link.
Expense Ratio
Month End Expense Ratios (Annualized)
Plan Base Expense Ratio (BER)
Regular1 1.24%
Direct 0.20%
BER excludes brokerage & transactioncost,and
statutory levies (including GST). For detailedTER,
visit:https://digital.camsonline.com/dnlresult/hsbc_ter_report.
xlsx
Portfolio Data
Top 10 Holdings % to Net
Assets
1 HSBC Large Cap Fund - Direct Growth 34.08%
2 HSBC Midcap Fund - Direct Growth 21.22%
3 HSBC Small Cap Fund - Direct Growth 21.07%
4 HSBC Medium to Long Term Fund - DG 9.94%
5 HSBC Corporate Bond Fund - Direct Growth 8.15%

[5] HSBC MF Factsheet (The Asset) - August 2026 · p.83 · published 2026-08-31
Managing Since Jun 30, 2014 / Jul 15, 2023 /
Feb 01, 2025/ Aug 26, 2026
Minimum Investment
Lumpsum Amount ₹Rs. 5000/- and in
multiples of Re. 1/-
SIP Amount : Please refer the table at the bottom of
thepage.
Load Structure
Exit Load:
Any redemption/switch-out of units on or before 1
month from the date of allotment: 0.25%
If units are redeemed or switched out after 1 Month
from the date of allotment: NIL(Effective date:
August 01,2023)
Expense Ratio
Month End Expense Ratios (Annualized)
Plan Base Expense Ratio (BER)
Regular1 0.75%
Direct 0.22%
BER excludes brokerage & transactioncost,and
statutory levies (including GST). For detailedTER,
visit:https://digital.camsonline.com/dnlresult/hsbc_ter_report.
xlsx
Quantitative Measures*
1 Standard Deviation (%) 0.54
2 Beta 0.67
3 Tracking Error (%)
1 Year NA
3 Years NA
4 Sharpe Ratio (%) 2.69
5 R2 0.61
6 Tracking Difference (%)
1 Year NA
3 Years NA
5 Years NA
Since Inception NA
7 Information Ratio NA
For more details refer next page for detailed
description in tabular format.
1Continuing plans
NA Stands for “Not Applicable”
Fund Performance (CAGR)
Compounded
Annualised
Returns
Scheme
Returns %
- Regular
Scheme
Returns %
- Direct
Benchmark
Returns %
Returns for last 1
year 5.85 6.43 7.02

Question: What is the exit load of HSBC Value Fund?

Answer only from the context above. Cite every fact with its source number, like [1].
```
