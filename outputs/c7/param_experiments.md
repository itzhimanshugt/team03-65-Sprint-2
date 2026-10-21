# C7 — Model parameters and output control

## 1. Temperature (same prompt, 3 runs each)

Prompt: _Write a one-line tagline for a compliance assistant for financial advisors._

| Temperature | Run 1 | Run 2 | Run 3 | Distinct |
|---|---|---|---|---|
| 0.0 | **Compliance made simple, so you can focus on your clients.** | **Compliance made simple, so you can focus on your clients.** | **Compliance made simple, so you can focus on your clients.** | 1/3 |
| 0.7 | **Compliance made simple, so you can focus on your clients.** | **Compliance simplified, so you can focus on your clients.** | Here are a few options, depending on the tone you want to set:  **Confidence-focused:** * "Compliance made effortless, so you can focus on your clients."  **Efficiency-focused:** * "Streamline your compliance, accelerate your growth."  ** | 3/3 |
| 1.5 | Here are a few options depending on your brand voice:  *   **Confidence-focused:** "Compliance made simple, so you can focus on your clients." *   **Action-oriented:** "Navigate regulatory complexity with absolute precision." *   **Safety-focused:** | Here are a few options, depending on the tone you want to set:  *   **Trust-based:** "Compliance made effortless, so you can focus on your clients." *   **Efficiency-based:** "The intelligence to keep you compliant, the speed to keep | **Stay compliant, stay focused—empowering advisors to grow with confidence.** | 3/3 |

## 2. max_tokens

Prompt: _Explain the NAV of a mutual fund in 3 sentences._

| max_tokens | finish_reason | Output tokens | Output |
|---|---|---|---|
| 20 | length | 16 | The Net Asset Value (NAV) represents the per-share market value of a |
| 60 | length | 56 | The Net Asset Value (NAV) represents the per-share market value of a mutual fund, calculated by subtracting the fund's total liabilities from the current market value of all its assets. This figure is determined at the end of each trading day by dividing the net assets by the |
| 300 | stop | 86 | The Net Asset Value (NAV) represents the per-share market value of a mutual fund, calculated by subtracting the fund's total liabilities from the total value of its assets. This figure is determined at the end of each trading day by dividing the net value of the fund's holdings by the total number of outstanding shares. Investors use the NAV to understand the price at which they can buy or sell shares of the fund. |

## 3. Stop sequence

| stop | finish_reason | Output |
|---|---|---|
| None | stop | The Net Asset Value (NAV) represents the per-share market value of a mutual fund, calculated by taking the total value of all the fund's assets minus its liabilities. This figure is determined at the end of each trading day by dividing the net assets by the total number of outstanding shares held by investors. Essentially, the NAV serves as the price at which investors can buy or sell units of the mutual fund. |
| ['.'] | stop | The Net Asset Value (NAV) represents the per-share market value of a mutual fund, calculated by subtracting the fund's total liabilities from the total value of its assets |

## 4. Hidden thinking tokens (Gemini reasoning)

| reasoning_effort | max_tokens | Visible output |
|---|---|---|
| none | 60 | The Net Asset Value (NAV) represents the per-share market value of a mutual fund, calculated by subtracting the fund's total liabilities from the total value of its assets. This figure is determined at the end of each trading day by dividing the net value of the portfolio by |
| low | 60 | The |