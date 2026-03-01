# finance

A CFA-level finance problem solver that follows an 8-step methodology for maximum accuracy and precision.

## Methodology

Every solver function produces a `SolverResult` that walks through all eight steps:

| Step | Description |
|------|-------------|
| **1** | Clearly identify what the question is asking |
| **2** | List all given inputs and define variables |
| **3** | State the correct financial formula(s) and explain why |
| **4** | Show all calculations step-by-step |
| **5** | Provide the exact Excel formula (using correct Excel syntax) |
| **6** | Cross-check the result using an alternative method |
| **7** | Sanity-check the final answer |
| **8** | Provide the final answer clearly labeled as `FINAL ANSWER: _______` |

## Supported Problem Types

| Module function | Finance topic |
|----------------|---------------|
| `future_value` | Future Value (FV) — lump sum & annuity |
| `present_value` | Present Value (PV) — lump sum & annuity |
| `number_of_periods` | Number of Periods (NPER) |
| `interest_rate` | Periodic Interest Rate (RATE) |
| `net_present_value` | Net Present Value (NPV) |
| `internal_rate_of_return` | Internal Rate of Return (IRR) |
| `bond_price` | Fixed-Coupon Bond Pricing |
| `bond_ytm` | Yield to Maturity (YTM) |
| `portfolio_statistics` | Weighted Mean, Variance, Std Dev |
| `capm_expected_return` | CAPM Expected Return |
| `straight_line_depreciation` | Straight-Line Depreciation (SLN) |
| `payback_period` | Payback Period |

## Quick Start

```python
from finance_solver import future_value, net_present_value, capm_expected_return

# Future value of $1,000 invested at 5% for 10 years
result = future_value(pv=1000, rate=0.05, nper=10)
print(result)

# NPV of a project with cash flows
result = net_present_value(
    rate=0.10,
    cash_flows=[-50000, 15000, 20000, 25000, 10000],
)
print(result)

# CAPM expected return
result = capm_expected_return(
    risk_free_rate=0.03,
    beta=1.2,
    market_return=0.10,
)
print(result)
```

### Example output

```
======================================================================
FINANCE PROBLEM SOLVER — 8-STEP METHODOLOGY
======================================================================

[1] QUESTION
    Calculate the Future Value (FV) of a cash flow.

[2] INPUTS & VARIABLES
    PV (Present Value) = 1000
    r (periodic rate) = 5.0000%
    n (periods) = 10
    PMT (payment) = 0
    Payment type = Ordinary Annuity

[3] FORMULA & RATIONALE
    FV = PV × (1 + r)^n
    Rationale: Compounding formula converts today's value to a future value. ...

[4] STEP-BY-STEP CALCULATIONS
    Step 1: FV of lump sum = 1000 × (1 + 0.05)^10 = 1628.894628
    Step 2: Total FV = 1628.894628

[5] EXCEL FORMULA
    =FV(0.05,10,0,-1000,0)

[6] CROSS-CHECK
    Iterative period-by-period accumulation yields 1628.894628. Match: True

[7] SANITY CHECK
    FV (1628.8946) > PV (1000), which is expected given rate = 5.00%.

======================================================================
FINAL ANSWER: 1628.8946
======================================================================
```

## Running Tests

```bash
python -m pytest tests/test_finance_solver.py -v
```
