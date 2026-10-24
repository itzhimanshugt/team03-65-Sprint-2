# C30 — Grounded vs ungrounded answers

Ungrounded = the same model with no documents, asked directly. Grounded = the full pipeline (retrieve → re-rank → numbered context → answer only from it).

## What is the riskometer level of HSBC Liquid Fund?

**Correct (from the corpus):** Low to Moderate (Aug 2026 factsheet, p.112)

**Ungrounded:** As of the latest disclosures, the **HSBC Liquid Fund** is categorized under the **"Low to Moderate"** risk level on the SEBI-mandated Riskometer.

Here is a breakdown of why it carries this classification:

### 1. Understanding the Riskometer
The SEBI Riskometer uses a six-level scale:
*   Low
*   **Low to Moderate**
*   Moderate
*   Moderately High
*   High
*   Very High

### 2. Why "Low to Moderate"?
*   **Asset Allocation:** Liquid funds are mandated to invest in debt and money market securities with a maturity of up to 91 days. Because the duration of the underlying assets is very short, the fund is less sensitive to interest rate fluctuations compared to long-term debt funds.
*   **Credit Quality:** These funds typically invest in high-rated (sovereign, AAA, or A1+) instruments, which minimizes the risk of default.
*   **Liquidity:** Because the underlying assets mature quickly, the fund maintains high liquidity, allowing for quick redemptions.

### Important Considerations:
*   **Not Risk-Free:** While "Low to Moderate" is on the safer end of the spectrum, it is not "risk-free." There is still a minor risk of interest rate changes or credit events (though rare in high-quality liquid funds).
*   **Dynamic Nature:** Riskometers are reviewed periodically. If the fund manager changes the portfolio composition or if market conditions shift significantly, the risk level could theoretically be adjusted by the Asset Management Company (AMC).
*   **Where to check:** You can always find the most current Riskometer rating on the **[HSBC Mutual Fund website](https://www.assetmanagement.hsbc.co.in/)** under the specific fund’s "Factsheet" or "Product Label" section.

***Disclaimer:** I am an AI, not a financial advisor. Mutual fund investments are subject to market risks. Please read all scheme-related documents carefully or consult with a SEBI-registered financial advisor before making investment decisions.*

**Grounded:** The scheme riskometer for the HSBC Liquid Fund is "Low to Moderate" [3].

**Grounded citations:** [3] hsbc-factsheet-2026-08.pdf p.112

## What is the exit load of Parag Parikh Liquid Fund on day 1?

**Correct (from the corpus):** 0.0070% (KIM, p.13)

**Ungrounded:** As of the current scheme information document, the **Parag Parikh Liquid Fund has an exit load of 0.0070%** if redeemed within 1 day of investment.

Here is the breakdown of the exit load structure for this fund:

*   **Day 1:** 0.0070%
*   **Day 2:** 0.0065%
*   **Day 3:** 0.0060%
*   **Day 4:** 0.0055%
*   **Day 5:** 0.0050%
*   **Day 6:** 0.0045%
*   **Day 7 onwards:** Nil

**Important Note:** Liquid funds are designed for very short-term parking of money. Because the exit load is applied on a sliding scale for the first week, it is generally recommended to hold the investment for at least 7 days to avoid any exit load charges.

*Disclaimer: Exit loads are subject to change by the Asset Management Company (AMC). It is always recommended to check the latest Scheme Information Document (SID) or the fund's page on the official PPFAS Mutual Fund website before making a transaction.*

**Grounded:** The exit load for the Parag Parikh Liquid Fund on Day 1 is 0.0070% [1], [4].

**Grounded citations:** [1] ppfas-factsheet-2026-09.pdf p.24, [4] ppfas-liquid-sid.pdf p.30

## How soon does compliance upload a new monthly factsheet?

**Correct (from the corpus):** Within 3 working days (firm FAQ)

**Ungrounded:** The timeline for a compliance team to upload a new monthly factsheet depends entirely on your firm’s **internal policies, regulatory requirements, and operational workflow.**

However, in the asset management and financial services industry, there are generally three "tiers" of turnaround times:

### 1. The "Standard" Industry Timeline (5–10 Business Days)
Most firms aim to have factsheets live on their website between the **5th and 10th business day** of the new month. 
*   **Why:** This allows time for the accounting team to finalize the month-end NAV (Net Asset Value), the investment team to write the commentary, and compliance to review the data and disclosures.

### 2. The "Fast-Track" Timeline (2–4 Business Days)
High-performing firms with automated reporting software and pre-approved "compliance templates" can often get factsheets live within a few days of month-end.
*   **Why:** These firms use "compliance-by-design" workflows where the data is pulled directly from a verified source (like a portfolio accounting system) into a template that has already been pre-cleared by compliance.

### 3. The "Regulatory/Manual" Timeline (10+ Business Days)
If your firm has a manual review process, complex multi-jurisdictional requirements (e.g., needing to comply with both SEC and ESMA/UCITS rules), or a high volume of funds, it can take two weeks or longer.
*   **Why:** If the factsheet requires manual verification of performance attribution, ESG data, or complex risk metrics, the compliance review process is significantly more time-consuming.

---

### Factors that influence your specific timeline:
If you are trying to determine when *your* firm’s factsheet will be ready, check these four things:

*   **The "Data Freeze" Date:** When does the accounting team finalize the month-end numbers? Compliance cannot review the factsheet until the data is "locked."
*   **The Review Queue:** Does your compliance team have a Service Level Agreement (SLA)? Many firms have an internal policy stating that compliance must review marketing materials within 48–72 hours of submission.
*   **The "Commentary" Bottleneck:** Often, the delay isn't compliance—it’s the Portfolio Manager taking too long to write the monthly market commentary.
*   **Automation:** Does your firm use a platform like Seismic, Seismic-Dox, or a proprietary automated system? If so, the process is likely much faster than firms using manual Excel-to-InDesign workflows.

### How to find out for sure:
1.  **Check the "Reporting Calendar":** Most operations or marketing teams maintain a calendar that lists the "Factsheet Publication Date."
2.  **Ask

**Grounded:** Compliance uploads the new factsheet within 3 working days of its publication by the fund house [1].

**Grounded citations:** [1] firm-faq.md p.3
