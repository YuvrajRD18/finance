"""
Finance Problem Solver
======================
A CFA-level finance problem solver that follows an 8-step methodology:
  1. Identify what the question is asking
  2. List all given inputs and define variables
  3. State the correct financial formula(s) and explain why
  4. Show all calculations step-by-step
  5. Provide the exact Excel formula
  6. Cross-check the result using an alternative method
  7. Sanity-check the final answer
  8. Provide the final answer labeled as: FINAL ANSWER: _______
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Core result container
# ---------------------------------------------------------------------------

@dataclass
class SolverResult:
    """Structured output of a finance solver following the 8-step methodology."""

    question_summary: str
    inputs: dict[str, Any]
    formula: str
    formula_explanation: str
    steps: list[str]
    excel_formula: str
    cross_check: str
    sanity_check: str
    final_answer: str
    final_answer_value: float | None = None
    assumptions: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines: list[str] = []
        lines.append("=" * 70)
        lines.append("FINANCE PROBLEM SOLVER — 8-STEP METHODOLOGY")
        lines.append("=" * 70)

        lines.append("\n[1] QUESTION")
        lines.append(f"    {self.question_summary}")

        lines.append("\n[2] INPUTS & VARIABLES")
        for k, v in self.inputs.items():
            lines.append(f"    {k} = {v}")

        lines.append("\n[3] FORMULA & RATIONALE")
        lines.append(f"    {self.formula}")
        lines.append(f"    Rationale: {self.formula_explanation}")

        lines.append("\n[4] STEP-BY-STEP CALCULATIONS")
        for i, step in enumerate(self.steps, 1):
            lines.append(f"    Step {i}: {step}")

        lines.append("\n[5] EXCEL FORMULA")
        lines.append(f"    {self.excel_formula}")

        lines.append("\n[6] CROSS-CHECK")
        lines.append(f"    {self.cross_check}")

        lines.append("\n[7] SANITY CHECK")
        lines.append(f"    {self.sanity_check}")

        if self.assumptions:
            lines.append("\n[*] ASSUMPTIONS")
            for a in self.assumptions:
                lines.append(f"    • {a}")

        lines.append("\n" + "=" * 70)
        lines.append(f"FINAL ANSWER: {self.final_answer}")
        lines.append("=" * 70)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Time Value of Money (TVM)
# ---------------------------------------------------------------------------

def future_value(
    pv: float,
    rate: float,
    nper: int,
    pmt: float = 0.0,
    pmt_type: int = 0,
) -> SolverResult:
    """
    Compute the Future Value of a lump sum or annuity.

    Parameters
    ----------
    pv   : present value (positive = cash inflow)
    rate : periodic interest rate (decimal, e.g. 0.05 for 5%)
    nper : number of periods
    pmt  : periodic payment (0 for lump-sum)
    pmt_type : 0 = end-of-period (ordinary annuity),
               1 = beginning-of-period (annuity due)
    """
    # FV of lump sum
    fv_lump = pv * (1 + rate) ** nper

    # FV of annuity
    if rate == 0:
        fv_ann = pmt * nper
    else:
        fv_ann = pmt * (((1 + rate) ** nper - 1) / rate)
        if pmt_type == 1:
            fv_ann *= (1 + rate)

    fv = fv_lump + fv_ann

    # Cross-check via iterative accumulation
    balance = pv
    for _ in range(nper):
        if pmt_type == 1:
            balance += pmt
        balance *= (1 + rate)
        if pmt_type == 0:
            balance += pmt
    cross_check_value = balance
    cross_check_match = abs(fv - cross_check_value) < 1e-6

    annuity_type = "Annuity Due" if pmt_type == 1 else "Ordinary Annuity"
    excel_pmt_type = pmt_type
    excel = (
        f"=FV({rate},{nper},{-pmt},{-pv},{excel_pmt_type})"
    )

    steps = [
        f"FV of lump sum = {pv} × (1 + {rate})^{nper} = {fv_lump:.6f}",
    ]
    if pmt != 0:
        steps.append(f"FV of {annuity_type} = {pmt} × [((1+{rate})^{nper} - 1) / {rate}]"
                     + (f" × (1+{rate})" if pmt_type == 1 else "")
                     + f" = {fv_ann:.6f}")
        steps.append(f"Total FV = {fv_lump:.6f} + {fv_ann:.6f} = {fv:.6f}")
    else:
        steps.append(f"Total FV = {fv:.6f}")

    sanity = (
        f"FV ({fv:.4f}) {'>' if fv > pv else '<'} PV ({pv}), which is "
        f"{'expected' if (rate > 0 and fv > pv) or (rate < 0 and fv < pv) else 'unexpected'} "
        f"given rate = {rate:.2%}."
    )

    formula_str = "FV = PV × (1 + r)^n" + (" + PMT × [((1+r)^n - 1)/r]" + (" × (1+r)" if pmt_type == 1 else "") if pmt != 0 else "")

    return SolverResult(
        question_summary="Calculate the Future Value (FV) of a cash flow.",
        inputs={
            "PV (Present Value)": pv,
            "r (periodic rate)": f"{rate:.4%}",
            "n (periods)": nper,
            "PMT (payment)": pmt,
            "Payment type": annuity_type,
        },
        formula=formula_str,
        formula_explanation=(
            "Compounding formula converts today's value to a future value. "
            "The annuity component accumulates periodic payments at compound interest."
        ),
        steps=steps,
        excel_formula=excel,
        cross_check=(
            f"Iterative period-by-period accumulation yields {cross_check_value:.6f}. "
            f"Match: {cross_check_match}"
        ),
        sanity_check=sanity,
        final_answer=f"{fv:.4f}",
        final_answer_value=fv,
    )


def present_value(
    fv: float,
    rate: float,
    nper: int,
    pmt: float = 0.0,
    pmt_type: int = 0,
) -> SolverResult:
    """
    Compute the Present Value of a lump sum or annuity.

    Parameters
    ----------
    fv   : future value (0 for pure annuity)
    rate : periodic interest rate (decimal)
    nper : number of periods
    pmt  : periodic payment
    pmt_type : 0 = ordinary annuity, 1 = annuity due
    """
    if rate == 0:
        discount_factor = 1.0
        pv_lump = fv
        pv_ann = pmt * nper
    else:
        discount_factor = 1 / (1 + rate) ** nper
        pv_lump = fv * discount_factor
        pv_ann = pmt * ((1 - (1 + rate) ** (-nper)) / rate)
        if pmt_type == 1:
            pv_ann *= (1 + rate)

    pv = pv_lump + pv_ann

    annuity_type = "Annuity Due" if pmt_type == 1 else "Ordinary Annuity"
    excel = f"=PV({rate},{nper},{-pmt},{-fv},{pmt_type})"

    steps = [
        f"Discount factor = 1 / (1 + {rate})^{nper} = {discount_factor:.6f}",
        f"PV of lump sum (FV) = {fv} × {discount_factor:.6f} = {pv_lump:.6f}",
    ]
    if pmt != 0:
        steps.append(
            f"PV of {annuity_type} = {pmt} × [(1 - (1+{rate})^-{nper}) / {rate}]"
            + (f" × (1+{rate})" if pmt_type == 1 else "")
            + f" = {pv_ann:.6f}"
        )
        steps.append(f"Total PV = {pv_lump:.6f} + {pv_ann:.6f} = {pv:.6f}")
    else:
        steps.append(f"Total PV = {pv:.6f}")

    # Cross-check: grow PV forward and compare to FV
    fv_check = pv * (1 + rate) ** nper
    if pmt != 0:
        fv_ann_check = pmt * (((1 + rate) ** nper - 1) / rate) if rate != 0 else pmt * nper
        if pmt_type == 1:
            fv_ann_check *= (1 + rate)
        fv_check += fv_ann_check
    cross_check_match = abs(fv_check - fv) < 1e-4

    sanity = (
        f"PV ({pv:.4f}) {'<' if pv < fv else '>'} FV ({fv}), which is "
        f"{'expected' if rate >= 0 else 'unexpected'} given positive discount rate."
    )

    formula_str = "PV = FV / (1 + r)^n" + (" + PMT × [(1-(1+r)^-n)/r]" + (" × (1+r)" if pmt_type == 1 else "") if pmt != 0 else "")

    return SolverResult(
        question_summary="Calculate the Present Value (PV) of a cash flow.",
        inputs={
            "FV (Future Value)": fv,
            "r (periodic rate)": f"{rate:.4%}",
            "n (periods)": nper,
            "PMT (payment)": pmt,
            "Payment type": annuity_type,
        },
        formula=formula_str,
        formula_explanation=(
            "Discounting converts a future value back to its present equivalent. "
            "The annuity PVA formula sums discounted periodic payments."
        ),
        steps=steps,
        excel_formula=excel,
        cross_check=(
            f"Growing PV forward gives FV = {fv_check:.4f} vs target FV = {fv}. "
            f"Match: {cross_check_match}"
        ),
        sanity_check=sanity,
        final_answer=f"{pv:.4f}",
        final_answer_value=pv,
    )


def number_of_periods(
    pv: float,
    fv: float,
    rate: float,
    pmt: float = 0.0,
    pmt_type: int = 0,
) -> SolverResult:
    """
    Compute the Number of Periods (NPER) needed to reach a future value.

    Parameters
    ----------
    pv   : present value (negative for cash outflow convention)
    fv   : future value
    rate : periodic interest rate (decimal)
    pmt  : periodic payment (0 for lump-sum)
    pmt_type : 0 = ordinary annuity, 1 = annuity due
    """
    if rate == 0:
        if pmt == 0:
            raise ValueError("Cannot solve for NPER when rate=0 and pmt=0.")
        nper = (fv - pv) / pmt
    else:
        # Solve: fv + pv*(1+r)^n + pmt*(1+r*pmt_type)*((1+r)^n - 1)/r = 0
        # Rearranging: (pv + A)*(1+r)^n = A - fv, where A = pmt*(1+r*pmt_type)/r
        # => (1+r)^n = (A - fv) / (pv + A)
        pmt_factor = pmt * (1 + rate * pmt_type) / rate
        numerator = pmt_factor - fv
        denominator = pv + pmt_factor
        if denominator == 0 or (numerator / denominator) <= 0:
            raise ValueError(
                "Cannot solve for NPER with the given inputs "
                "(no finite solution exists)."
            )
        nper = math.log(numerator / denominator) / math.log(1 + rate)

    excel = f"=NPER({rate},{-pmt},{pv},{fv},{pmt_type})"

    if rate == 0:
        steps = [
            "Rate = 0: n = (FV - PV) / PMT",
            f"n = ({fv} - {pv}) / {pmt} = {nper:.6f} periods",
        ]
    else:
        pmt_factor = pmt * (1 + rate * pmt_type) / rate
        steps = [
            "Using NPER formula: n = ln((PMT×(1+r×type)/r - FV) / (PV + PMT×(1+r×type)/r)) / ln(1+r)",
            f"n = ln({pmt_factor - fv:.6f} / {pv + pmt_factor:.6f}) / ln({1 + rate:.6f})",
            f"n = {nper:.6f} periods",
        ]

    cross_check_fv = future_value(pv, rate, int(round(nper)), pmt, pmt_type).final_answer_value
    cross_match = abs((cross_check_fv or 0) - fv) < 0.01

    sanity = (
        f"n = {nper:.4f} periods is {'positive, which makes sense' if nper > 0 else 'negative — check inputs'}."
    )

    return SolverResult(
        question_summary="Calculate the Number of Periods (NPER) to reach a target value.",
        inputs={
            "PV (Present Value)": pv,
            "FV (Future Value)": fv,
            "r (periodic rate)": f"{rate:.4%}",
            "PMT (payment)": pmt,
            "Payment type": "Annuity Due" if pmt_type == 1 else "Ordinary Annuity",
        },
        formula="n = ln(-(FV + PMT×(1+r×type)/r) / (PV + PMT×(1+r×type)/r)) / ln(1+r)",
        formula_explanation=(
            "Derived by solving the TVM equation for n using logarithms."
        ),
        steps=steps,
        excel_formula=excel,
        cross_check=(
            f"FV using rounded n={round(nper)} periods: {cross_check_fv:.4f} vs target {fv}. "
            f"Match: {cross_match}"
        ),
        sanity_check=sanity,
        final_answer=f"{nper:.4f} periods",
        final_answer_value=nper,
    )


def interest_rate(
    pv: float,
    fv: float,
    nper: int,
    pmt: float = 0.0,
    pmt_type: int = 0,
    guess: float = 0.1,
    tol: float = 1e-8,
    max_iter: int = 1000,
) -> SolverResult:
    """
    Compute the periodic Interest Rate using Newton-Raphson iteration.

    Parameters
    ----------
    pv       : present value
    fv       : future value
    nper     : number of periods
    pmt      : periodic payment
    pmt_type : 0 = ordinary annuity, 1 = annuity due
    guess    : initial rate guess (default 10%)
    """
    def f(r: float) -> float:
        if r == 0:
            return pv + pmt * nper + fv
        return (
            pv * (1 + r) ** nper
            + pmt * (1 + r * pmt_type) * ((1 + r) ** nper - 1) / r
            + fv
        )

    def df(r: float) -> float:
        eps = 1e-7
        return (f(r + eps) - f(r - eps)) / (2 * eps)

    r = guess
    for iteration in range(max_iter):
        fx = f(r)
        dfx = df(r)
        if dfx == 0:
            break
        r_new = r - fx / dfx
        if abs(r_new - r) < tol:
            r = r_new
            break
        r = r_new

    excel = f"=RATE({nper},{-pmt},{pv},{fv},{pmt_type},{guess})"

    steps = [
        "Solve TVM equation for r using Newton-Raphson iteration:",
        f"  PV×(1+r)^n + PMT×(1+r×type)×((1+r)^n-1)/r + FV = 0",
        f"  Initial guess: r = {guess:.4%}",
        f"  Converged to: r = {r:.8f}",
        f"  r = {r:.6f} = {r:.4%} per period",
    ]

    # Cross-check: compute FV with the solved rate
    fv_check = future_value(pv, r, nper, pmt, pmt_type).final_answer_value
    # For cross-check, fv_check should equal -fv (sign convention)
    cross_match = abs((fv_check or 0) + fv) < 0.01 or abs((fv_check or 0) - fv) < 0.01

    sanity = (
        f"Rate of {r:.4%} per period is {'positive, which makes sense for growth' if r > 0 else 'negative (check inputs)'}."
    )

    return SolverResult(
        question_summary="Calculate the periodic Interest Rate (RATE).",
        inputs={
            "PV (Present Value)": pv,
            "FV (Future Value)": fv,
            "n (periods)": nper,
            "PMT (payment)": pmt,
            "Payment type": "Annuity Due" if pmt_type == 1 else "Ordinary Annuity",
            "Initial guess": f"{guess:.4%}",
        },
        formula="PV×(1+r)^n + PMT×(1+r×type)×((1+r)^n-1)/r + FV = 0  →  solve for r",
        formula_explanation=(
            "The TVM equation is solved numerically for r (Newton-Raphson), "
            "matching Excel's RATE function."
        ),
        steps=steps,
        excel_formula=excel,
        cross_check=(
            f"Computing FV with solved rate: {fv_check:.4f} vs target FV = {fv}. "
            f"Match: {cross_match}"
        ),
        sanity_check=sanity,
        final_answer=f"{r:.6f} ({r:.4%} per period)",
        final_answer_value=r,
    )


# ---------------------------------------------------------------------------
# Net Present Value & Internal Rate of Return
# ---------------------------------------------------------------------------

def net_present_value(
    rate: float,
    cash_flows: list[float],
    initial_investment: float | None = None,
) -> SolverResult:
    """
    Compute the Net Present Value (NPV) of a series of cash flows.

    Parameters
    ----------
    rate             : discount rate per period (decimal)
    cash_flows       : list of cash flows; if initial_investment is None,
                       the first element is treated as the t=0 outlay.
    initial_investment : optional explicit t=0 investment (negative outflow).
    """
    if initial_investment is not None:
        cf0 = initial_investment
        future_cfs = cash_flows
    else:
        cf0 = cash_flows[0]
        future_cfs = cash_flows[1:]

    npv = cf0 + sum(
        cf / (1 + rate) ** t for t, cf in enumerate(future_cfs, start=1)
    )

    # Excel NPV does NOT include t=0; user must add it separately
    excel_cf_args = ",".join(str(c) for c in future_cfs)
    excel = f"={cf0}+NPV({rate},{excel_cf_args})"

    steps = ["NPV = CF₀ + Σ [CFₜ / (1+r)^t]"]
    steps.append(f"  CF₀ = {cf0}")
    for t, cf in enumerate(future_cfs, start=1):
        pv_t = cf / (1 + rate) ** t
        steps.append(f"  t={t}: {cf} / (1+{rate})^{t} = {pv_t:.4f}")
    steps.append(f"  NPV = {npv:.4f}")

    # Cross-check: discount via cumulative factor
    npv_check = cf0
    for t, cf in enumerate(future_cfs, start=1):
        npv_check += cf * (1 + rate) ** (-t)
    cross_match = abs(npv_check - npv) < 1e-6

    sanity = (
        f"NPV = {npv:.4f} is {'positive → project creates value' if npv > 0 else 'negative → project destroys value' if npv < 0 else 'zero → break-even'}."
    )

    all_cfs = [cf0] + list(future_cfs)
    return SolverResult(
        question_summary="Calculate the Net Present Value (NPV) of a project.",
        inputs={
            "r (discount rate)": f"{rate:.4%}",
            "Cash flows": all_cfs,
        },
        formula="NPV = Σ [CFₜ / (1+r)^t]  for t = 0, 1, …, n",
        formula_explanation=(
            "NPV discounts each future cash flow to t=0 and sums them. "
            "A positive NPV indicates value creation above the required return."
        ),
        steps=steps,
        excel_formula=excel,
        cross_check=f"Alternative discount calculation: {npv_check:.4f}. Match: {cross_match}",
        sanity_check=sanity,
        final_answer=f"{npv:.4f}",
        final_answer_value=npv,
    )


def internal_rate_of_return(
    cash_flows: list[float],
    guess: float = 0.1,
    tol: float = 1e-8,
    max_iter: int = 1000,
) -> SolverResult:
    """
    Compute the Internal Rate of Return (IRR) for a series of cash flows.

    Parameters
    ----------
    cash_flows : list of cash flows starting at t=0
    guess      : initial guess for the rate
    """
    def npv_func(r: float) -> float:
        return sum(cf / (1 + r) ** t for t, cf in enumerate(cash_flows))

    def npv_deriv(r: float) -> float:
        eps = 1e-7
        return (npv_func(r + eps) - npv_func(r - eps)) / (2 * eps)

    r = guess
    for _ in range(max_iter):
        fx = npv_func(r)
        dfx = npv_deriv(r)
        if dfx == 0:
            break
        r_new = r - fx / dfx
        if abs(r_new - r) < tol:
            r = r_new
            break
        r = r_new

    npv_at_irr = npv_func(r)

    cf_args = ",".join(str(c) for c in cash_flows)
    excel = f"=IRR({{{cf_args}}},{guess})"

    steps = [
        "Set NPV = 0: Σ [CFₜ / (1+IRR)^t] = 0",
        f"Initial guess: r = {guess:.4%}",
        f"Newton-Raphson converged to: IRR = {r:.8f}",
        f"NPV at IRR = {npv_at_irr:.2e} (should be ≈ 0)",
    ]

    # Cross-check: compute NPV at IRR ± 1bps
    npv_low = npv_func(r - 0.0001)
    npv_high = npv_func(r + 0.0001)
    cross = f"NPV(IRR-1bp)={npv_low:.4f}, NPV(IRR+1bp)={npv_high:.4f} — sign change confirms root."

    sanity = (
        f"IRR = {r:.4%}. "
        f"{'Higher than a typical hurdle rate — likely acceptable project.' if r > 0.10 else 'Below 10% — compare to cost of capital.'}"
    )

    return SolverResult(
        question_summary="Calculate the Internal Rate of Return (IRR).",
        inputs={
            "Cash flows (t=0,1,…)": cash_flows,
            "Initial guess": f"{guess:.4%}",
        },
        formula="Σ [CFₜ / (1+IRR)^t] = 0  →  solve for IRR",
        formula_explanation=(
            "IRR is the discount rate that makes NPV = 0. "
            "It is solved numerically since no closed-form solution exists for n > 2."
        ),
        steps=steps,
        excel_formula=excel,
        cross_check=cross,
        sanity_check=sanity,
        final_answer=f"{r:.6f} ({r:.4%})",
        final_answer_value=r,
    )


# ---------------------------------------------------------------------------
# Bond pricing & yield
# ---------------------------------------------------------------------------

def bond_price(
    face_value: float,
    coupon_rate: float,
    periods: int,
    ytm: float,
    frequency: int = 2,
) -> SolverResult:
    """
    Compute the price of a fixed-coupon bond.

    Parameters
    ----------
    face_value   : par / face value
    coupon_rate  : annual coupon rate (decimal)
    periods      : total number of coupon periods
    ytm          : annual yield to maturity (decimal)
    frequency    : coupon payments per year (1=annual, 2=semi-annual)
    """
    periodic_coupon = face_value * coupon_rate / frequency
    periodic_ytm = ytm / frequency

    # Price = PV of coupons + PV of face value
    if periodic_ytm == 0:
        pv_coupons = periodic_coupon * periods
    else:
        pv_coupons = periodic_coupon * (1 - (1 + periodic_ytm) ** (-periods)) / periodic_ytm

    pv_face = face_value / (1 + periodic_ytm) ** periods
    price = pv_coupons + pv_face

    # Excel: PRICE requires dates; use PV-based formula instead
    excel = (
        f"=PV({periodic_ytm},{periods},{-periodic_coupon},{-face_value},0)"
    )

    steps = [
        f"Periodic coupon = {face_value} × {coupon_rate:.4%} / {frequency} = {periodic_coupon:.4f}",
        f"Periodic YTM = {ytm:.4%} / {frequency} = {periodic_ytm:.6f}",
        f"PV of coupons = {periodic_coupon} × [1 - (1+{periodic_ytm:.6f})^-{periods}] / {periodic_ytm:.6f} = {pv_coupons:.4f}",
        f"PV of face value = {face_value} / (1+{periodic_ytm:.6f})^{periods} = {pv_face:.4f}",
        f"Bond Price = {pv_coupons:.4f} + {pv_face:.4f} = {price:.4f}",
    ]

    # Cross-check: sum individual PV of each cash flow
    check_price = sum(
        periodic_coupon / (1 + periodic_ytm) ** t for t in range(1, periods + 1)
    ) + face_value / (1 + periodic_ytm) ** periods
    cross_match = abs(check_price - price) < 0.001

    sanity = (
        f"Bond price = {price:.4f}. "
        f"{'Trading at a DISCOUNT (price < par) because coupon rate < YTM.' if price < face_value else 'Trading at a PREMIUM (price > par) because coupon rate > YTM.' if price > face_value else 'Trading at PAR.'}"
    )

    return SolverResult(
        question_summary="Calculate the price of a fixed-coupon bond.",
        inputs={
            "Face Value": face_value,
            "Annual Coupon Rate": f"{coupon_rate:.4%}",
            "Total Coupon Periods": periods,
            "Annual YTM": f"{ytm:.4%}",
            "Payment Frequency": f"{frequency}x per year",
            "Periodic Coupon": f"{periodic_coupon:.4f}",
            "Periodic YTM": f"{periodic_ytm:.6f}",
        },
        formula="Price = Σ [C/(1+y)^t] + F/(1+y)^n  =  C × PVIFA(y,n) + F × PVIF(y,n)",
        formula_explanation=(
            "A bond's fair price equals the present value of all future cash flows "
            "(coupon payments + face value repayment) discounted at the YTM."
        ),
        steps=steps,
        excel_formula=excel,
        cross_check=f"Sum of individual cash-flow PVs = {check_price:.4f}. Match: {cross_match}",
        sanity_check=sanity,
        final_answer=f"{price:.4f}",
        final_answer_value=price,
    )


def bond_ytm(
    face_value: float,
    coupon_rate: float,
    periods: int,
    price: float,
    frequency: int = 2,
    guess: float = 0.05,
    tol: float = 1e-8,
    max_iter: int = 1000,
) -> SolverResult:
    """
    Compute the Yield to Maturity (YTM) of a bond given its price.

    Parameters
    ----------
    face_value  : par / face value
    coupon_rate : annual coupon rate (decimal)
    periods     : total number of coupon periods
    price       : current market price
    frequency   : coupon payments per year
    """
    periodic_coupon = face_value * coupon_rate / frequency

    def price_func(periodic_y: float) -> float:
        if periodic_y == 0:
            return periodic_coupon * periods + face_value - price
        pv_c = periodic_coupon * (1 - (1 + periodic_y) ** (-periods)) / periodic_y
        pv_f = face_value / (1 + periodic_y) ** periods
        return pv_c + pv_f - price

    def price_deriv(periodic_y: float) -> float:
        eps = 1e-7
        return (price_func(periodic_y + eps) - price_func(periodic_y - eps)) / (2 * eps)

    py = guess / frequency
    for _ in range(max_iter):
        fx = price_func(py)
        dfx = price_deriv(py)
        if dfx == 0:
            break
        py_new = py - fx / dfx
        if abs(py_new - py) < tol:
            py = py_new
            break
        py = py_new

    ytm = py * frequency

    excel = f"=YIELD(settlement, maturity, {coupon_rate}, {price/face_value}, 1, {frequency})"

    steps = [
        f"Periodic coupon = {face_value} × {coupon_rate:.4%} / {frequency} = {periodic_coupon:.4f}",
        f"Solve: Price = Σ [C/(1+y_p)^t] + F/(1+y_p)^n  for y_p (periodic yield)",
        f"Newton-Raphson converged to: y_p = {py:.8f}",
        f"Annual YTM = y_p × {frequency} = {py:.8f} × {frequency} = {ytm:.6f}",
    ]

    price_check = bond_price(face_value, coupon_rate, periods, ytm, frequency).final_answer_value
    cross_match = abs((price_check or 0) - price) < 0.01

    sanity = (
        f"YTM = {ytm:.4%}. "
        f"{'Bond at discount → YTM > coupon rate ✓' if price < face_value else 'Bond at premium → YTM < coupon rate ✓' if price > face_value else 'Bond at par → YTM = coupon rate ✓'}"
    )

    return SolverResult(
        question_summary="Calculate the Yield to Maturity (YTM) of a bond.",
        inputs={
            "Face Value": face_value,
            "Annual Coupon Rate": f"{coupon_rate:.4%}",
            "Total Coupon Periods": periods,
            "Market Price": price,
            "Payment Frequency": f"{frequency}x per year",
        },
        formula="Price = Σ [C/(1+y_p)^t] + F/(1+y_p)^n  →  solve for y_p, YTM = y_p × frequency",
        formula_explanation=(
            "YTM is the discount rate that equates the bond's price to the PV of its cash flows. "
            "Solved numerically since no closed-form exists for n > 2."
        ),
        steps=steps,
        excel_formula=excel,
        cross_check=f"Bond price at solved YTM = {price_check:.4f} vs market price = {price}. Match: {cross_match}",
        sanity_check=sanity,
        final_answer=f"{ytm:.6f} ({ytm:.4%} per year)",
        final_answer_value=ytm,
    )


# ---------------------------------------------------------------------------
# Statistics: Weighted Average, Variance, Standard Deviation
# ---------------------------------------------------------------------------

def portfolio_statistics(
    returns: list[float],
    weights: list[float] | None = None,
) -> SolverResult:
    """
    Compute weighted mean return, variance, and standard deviation.

    Parameters
    ----------
    returns : list of asset returns (decimal)
    weights : list of weights (must sum to 1); equal-weight if None
    """
    n = len(returns)
    if weights is None:
        weights = [1 / n] * n
        weight_desc = "Equal weights (1/n)"
    else:
        weight_desc = str(weights)

    if abs(sum(weights) - 1.0) > 1e-9:
        raise ValueError(f"Weights must sum to 1.0, got {sum(weights)}")

    mean_return = sum(w * r for w, r in zip(weights, returns))

    variance = sum(w * (r - mean_return) ** 2 for w, r in zip(weights, returns))
    std_dev = math.sqrt(variance)

    steps = [
        f"Weighted Mean = Σ(wᵢ × rᵢ) = {' + '.join(f'{w:.4f}×{r:.4f}' for w, r in zip(weights, returns))} = {mean_return:.6f}",
        f"Weighted Variance = Σ(wᵢ × (rᵢ - μ)²)",
    ]
    for w, r in zip(weights, returns):
        steps.append(f"  {w:.4f} × ({r:.4f} - {mean_return:.6f})² = {w * (r - mean_return) ** 2:.8f}")
    steps.append(f"Variance = {variance:.8f}")
    steps.append(f"Std Dev = √{variance:.8f} = {std_dev:.6f}")

    # Cross-check: NumPy-style unweighted for equal-weight case
    if all(abs(w - 1 / n) < 1e-9 for w in weights):
        mean_check = sum(returns) / n
        var_check = sum((r - mean_check) ** 2 for r in returns) / n  # population variance
        cross = f"Population mean = {mean_check:.6f}, Population variance = {var_check:.8f}. Match: {abs(mean_check - mean_return) < 1e-9}"
    else:
        cross = f"Sum of weights = {sum(weights):.8f} (must = 1.0 ✓)"

    excel_returns = ",".join(str(r) for r in returns)
    excel_weights = ",".join(str(w) for w in weights)
    excel = (
        f"Mean:    =SUMPRODUCT({{{excel_weights}}},{{{excel_returns}}})\n"
        f"    Variance: =SUMPRODUCT({{{excel_weights}}},({{returns}}-mean)^2)\n"
        f"    Std Dev: =SQRT(Variance)"
    )

    sanity = (
        f"Mean = {mean_return:.4%}, Std Dev = {std_dev:.4%}. "
        f"Std dev {'> mean in absolute terms — high relative dispersion.' if std_dev > abs(mean_return) else '< mean — relatively low dispersion.'}"
    )

    return SolverResult(
        question_summary="Calculate weighted mean return, variance, and standard deviation.",
        inputs={
            "Returns": [f"{r:.4%}" for r in returns],
            "Weights": weights,
            "Weight description": weight_desc,
        },
        formula="μ = Σ(wᵢrᵢ),  σ² = Σ(wᵢ(rᵢ-μ)²),  σ = √σ²",
        formula_explanation=(
            "Weighted statistics give each observation an importance proportional to "
            "its weight, appropriate for portfolio analytics."
        ),
        steps=steps,
        excel_formula=excel,
        cross_check=cross,
        sanity_check=sanity,
        final_answer=(
            f"Mean Return = {mean_return:.6f} ({mean_return:.4%}), "
            f"Variance = {variance:.8f}, "
            f"Std Dev = {std_dev:.6f} ({std_dev:.4%})"
        ),
        final_answer_value=mean_return,
    )


# ---------------------------------------------------------------------------
# CAPM: Expected Return
# ---------------------------------------------------------------------------

def capm_expected_return(
    risk_free_rate: float,
    beta: float,
    market_return: float,
) -> SolverResult:
    """
    Compute the expected return of an asset using CAPM.

    Parameters
    ----------
    risk_free_rate : risk-free rate (decimal)
    beta           : asset beta
    market_return  : expected market return (decimal)
    """
    equity_risk_premium = market_return - risk_free_rate
    expected_return = risk_free_rate + beta * equity_risk_premium

    steps = [
        f"Equity Risk Premium (ERP) = Market Return - Risk-Free Rate = {market_return:.4%} - {risk_free_rate:.4%} = {equity_risk_premium:.4%}",
        f"Expected Return = Rf + β × ERP = {risk_free_rate:.4%} + {beta} × {equity_risk_premium:.4%} = {expected_return:.4%}",
    ]

    # Cross-check: Security Market Line interpretation
    sml_return = risk_free_rate + beta * (market_return - risk_free_rate)
    cross_match = abs(sml_return - expected_return) < 1e-10

    sanity = (
        f"Expected return = {expected_return:.4%}. "
        f"{'Higher than market return because β > 1 (more systematic risk).' if beta > 1 else 'Lower than market return because β < 1 (less systematic risk).' if beta < 1 else 'Equal to market return because β = 1.'}"
    )

    excel = f"={risk_free_rate}+{beta}*({market_return}-{risk_free_rate})"

    return SolverResult(
        question_summary="Calculate the expected return of an asset using the Capital Asset Pricing Model (CAPM).",
        inputs={
            "Risk-Free Rate (Rf)": f"{risk_free_rate:.4%}",
            "Beta (β)": beta,
            "Expected Market Return (Rm)": f"{market_return:.4%}",
            "Equity Risk Premium (Rm-Rf)": f"{equity_risk_premium:.4%}",
        },
        formula="E(Rᵢ) = Rf + βᵢ × (Rm - Rf)",
        formula_explanation=(
            "CAPM states that an asset's expected return equals the risk-free rate plus "
            "a risk premium proportional to the asset's systematic risk (beta). "
            "It assumes efficient markets and measures only non-diversifiable risk."
        ),
        steps=steps,
        excel_formula=excel,
        cross_check=f"SML calculation: {sml_return:.6f}. Match: {cross_match}",
        sanity_check=sanity,
        final_answer=f"{expected_return:.6f} ({expected_return:.4%})",
        final_answer_value=expected_return,
    )


# ---------------------------------------------------------------------------
# Depreciation
# ---------------------------------------------------------------------------

def straight_line_depreciation(
    cost: float,
    salvage_value: float,
    useful_life: int,
) -> SolverResult:
    """
    Compute straight-line depreciation.

    Parameters
    ----------
    cost          : initial cost of the asset
    salvage_value : estimated salvage value at end of life
    useful_life   : number of periods (years)
    """
    depreciation = (cost - salvage_value) / useful_life
    book_values = [cost - depreciation * t for t in range(useful_life + 1)]

    steps = [
        f"Depreciable Base = Cost - Salvage = {cost} - {salvage_value} = {cost - salvage_value}",
        f"Annual Depreciation = {cost - salvage_value} / {useful_life} = {depreciation:.4f}",
        "Book Value Schedule:",
    ]
    for t in range(useful_life + 1):
        steps.append(f"  Year {t}: Book Value = {book_values[t]:.4f}")

    cross_check_total = depreciation * useful_life
    cross_match = abs(cross_check_total - (cost - salvage_value)) < 1e-6

    sanity = (
        f"Annual depreciation = {depreciation:.4f}. "
        f"Total depreciation = {cross_check_total:.4f} = Depreciable base = {cost - salvage_value}. "
        f"{'✓' if cross_match else '✗'}"
    )

    excel = f"=SLN({cost},{salvage_value},{useful_life})"

    return SolverResult(
        question_summary="Calculate straight-line depreciation for an asset.",
        inputs={
            "Cost": cost,
            "Salvage Value": salvage_value,
            "Useful Life (years)": useful_life,
        },
        formula="Depreciation = (Cost - Salvage) / Useful Life",
        formula_explanation=(
            "Straight-line depreciation allocates equal depreciation expense each period, "
            "the simplest and most commonly used method."
        ),
        steps=steps,
        excel_formula=excel,
        cross_check=f"Total depreciation = {depreciation:.4f} × {useful_life} = {cross_check_total:.4f}. Match depreciable base: {cross_match}",
        sanity_check=sanity,
        final_answer=f"{depreciation:.4f} per year",
        final_answer_value=depreciation,
    )


# ---------------------------------------------------------------------------
# Payback Period
# ---------------------------------------------------------------------------

def payback_period(
    initial_investment: float,
    cash_flows: list[float],
) -> SolverResult:
    """
    Compute the Payback Period for a project.

    Parameters
    ----------
    initial_investment : initial outlay (positive number, represents an outflow)
    cash_flows         : list of periodic cash inflows (t=1, 2, …)
    """
    cumulative = 0.0
    payback = None
    cumulative_values: list[float] = [0.0] * (len(cash_flows) + 1)
    cumulative_values[0] = -initial_investment

    for t, cf in enumerate(cash_flows, start=1):
        cumulative += cf
        cumulative_values[t] = cumulative - initial_investment
        if payback is None and cumulative >= initial_investment:
            recovered_before = cumulative - cf
            fraction = (initial_investment - recovered_before) / cf
            payback = (t - 1) + fraction

    steps = ["Cumulative Cash Flow table:"]
    running = 0.0
    for t, cf in enumerate(cash_flows, start=1):
        running += cf
        steps.append(f"  End of Year {t}: Cumulative = {running:.4f}  (need {initial_investment})")
    if payback is not None:
        steps.append(f"Payback occurs in year {int(payback) + 1} — exact payback = {payback:.4f} years")
    else:
        steps.append("Investment is NOT recovered within the given cash flow horizon.")

    cross_check = (
        f"Verified: cumulative at end of period {int(payback):.0f} (last full period before payback) "
        f"= {cumulative_values[int(payback)]:.4f} (< 0, not yet recovered) and "
        f"at end of period {min(int(payback)+1, len(cumulative_values)-1):.0f} "
        f"= {cumulative_values[min(int(payback)+1, len(cumulative_values)-1)]:.4f} (≥ 0, recovered)."
        if payback is not None else "Not recovered."
    )

    sanity = (
        f"Payback period = {payback:.4f} years. "
        f"Shorter is better; compare to management's maximum acceptable payback."
        if payback is not None else "Project does not pay back within horizon."
    )

    excel = "=No direct Excel function; use cumulative sum table manually."

    return SolverResult(
        question_summary="Calculate the Payback Period of a project.",
        inputs={
            "Initial Investment": initial_investment,
            "Cash Flows (t=1,2,…)": cash_flows,
        },
        formula="Payback = Last full year + (Remaining / Next year CF)",
        formula_explanation=(
            "The payback period is the time required to recover the initial investment "
            "from cumulative cash inflows. It ignores time value and post-payback cash flows."
        ),
        steps=steps,
        excel_formula=excel,
        cross_check=cross_check,
        sanity_check=sanity,
        final_answer=f"{payback:.4f} years" if payback is not None else "Not recovered within horizon",
        final_answer_value=payback,
        assumptions=[
            "Cash flows occur at end of each period.",
            "Payback ignores time value of money (use Discounted Payback for TVM-adjusted analysis).",
        ],
    )
