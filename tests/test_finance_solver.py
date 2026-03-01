"""
Tests for finance_solver module.
Each test validates:
  - Correct numerical result
  - SolverResult structure (all 8-step fields populated)
  - Excel formula string presence
  - Final answer label format
"""

import math
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from finance_solver import (
    SolverResult,
    future_value,
    present_value,
    number_of_periods,
    interest_rate,
    net_present_value,
    internal_rate_of_return,
    bond_price,
    bond_ytm,
    portfolio_statistics,
    capm_expected_return,
    straight_line_depreciation,
    payback_period,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def assert_result_structure(result: SolverResult) -> None:
    """Verify that all 8 methodology fields are present and non-empty."""
    assert result.question_summary, "question_summary missing"
    assert result.inputs, "inputs missing"
    assert result.formula, "formula missing"
    assert result.formula_explanation, "formula_explanation missing"
    assert result.steps, "steps missing"
    assert result.excel_formula, "excel_formula missing"
    assert result.cross_check, "cross_check missing"
    assert result.sanity_check, "sanity_check missing"
    assert result.final_answer, "final_answer missing"
    # The string representation must contain "FINAL ANSWER:"
    assert "FINAL ANSWER:" in str(result)


# ---------------------------------------------------------------------------
# Future Value
# ---------------------------------------------------------------------------

class TestFutureValue:
    def test_lump_sum(self):
        """FV of $1,000 at 5% for 10 years = 1,628.8946"""
        result = future_value(pv=1000, rate=0.05, nper=10)
        assert_result_structure(result)
        assert result.final_answer_value is not None
        assert abs(result.final_answer_value - 1628.8946) < 0.01

    def test_ordinary_annuity(self):
        """FV of $100/period ordinary annuity at 5% for 5 periods."""
        result = future_value(pv=0, rate=0.05, nper=5, pmt=100, pmt_type=0)
        assert_result_structure(result)
        # FV = 100 * ((1.05^5 - 1) / 0.05) = 552.5631
        assert abs(result.final_answer_value - 552.5631) < 0.01

    def test_annuity_due(self):
        """FV of $100/period annuity-due at 5% for 5 periods."""
        result = future_value(pv=0, rate=0.05, nper=5, pmt=100, pmt_type=1)
        assert_result_structure(result)
        # Annuity due FV = ordinary FV × (1+r) = 552.5631 × 1.05 = 580.1913
        assert abs(result.final_answer_value - 580.1913) < 0.01

    def test_zero_rate(self):
        """FV with zero interest rate equals PV + sum of payments."""
        result = future_value(pv=1000, rate=0.0, nper=5, pmt=100)
        assert abs(result.final_answer_value - 1500.0) < 1e-9

    def test_combined_pv_and_pmt(self):
        """FV with both PV and periodic payments."""
        result = future_value(pv=500, rate=0.06, nper=3, pmt=100, pmt_type=0)
        assert_result_structure(result)
        fv_lump = 500 * 1.06 ** 3
        fv_ann = 100 * ((1.06 ** 3 - 1) / 0.06)
        expected = fv_lump + fv_ann
        assert abs(result.final_answer_value - expected) < 0.001

    def test_excel_formula_present(self):
        result = future_value(pv=1000, rate=0.05, nper=10)
        assert "=FV(" in result.excel_formula


# ---------------------------------------------------------------------------
# Present Value
# ---------------------------------------------------------------------------

class TestPresentValue:
    def test_lump_sum(self):
        """PV of $1,000 received in 5 years at 8% discount rate."""
        result = present_value(fv=1000, rate=0.08, nper=5)
        assert_result_structure(result)
        expected = 1000 / 1.08 ** 5
        assert abs(result.final_answer_value - expected) < 0.001

    def test_ordinary_annuity(self):
        """PV of $200/yr ordinary annuity at 6% for 4 years."""
        result = present_value(fv=0, rate=0.06, nper=4, pmt=200, pmt_type=0)
        assert_result_structure(result)
        expected = 200 * (1 - 1.06 ** (-4)) / 0.06
        assert abs(result.final_answer_value - expected) < 0.001

    def test_annuity_due(self):
        """PV annuity due is (1+r) times ordinary annuity PV."""
        ord_result = present_value(fv=0, rate=0.06, nper=4, pmt=200, pmt_type=0)
        due_result = present_value(fv=0, rate=0.06, nper=4, pmt=200, pmt_type=1)
        assert abs(due_result.final_answer_value - ord_result.final_answer_value * 1.06) < 0.001

    def test_excel_formula_present(self):
        result = present_value(fv=1000, rate=0.08, nper=5)
        assert "=PV(" in result.excel_formula


# ---------------------------------------------------------------------------
# Number of Periods
# ---------------------------------------------------------------------------

class TestNumberOfPeriods:
    def test_lump_sum_growth(self):
        """How many years to double $1,000 at 7%?"""
        result = number_of_periods(pv=-1000, fv=2000, rate=0.07)
        assert_result_structure(result)
        expected = math.log(2) / math.log(1.07)
        assert abs(result.final_answer_value - expected) < 0.001

    def test_annuity(self):
        """How many $300 payments at 5% to pay off $1,000 PV?"""
        result = number_of_periods(pv=-1000, fv=0, rate=0.05, pmt=300)
        assert_result_structure(result)
        assert result.final_answer_value > 0

    def test_excel_formula_present(self):
        result = number_of_periods(pv=-1000, fv=2000, rate=0.07)
        assert "=NPER(" in result.excel_formula


# ---------------------------------------------------------------------------
# Interest Rate
# ---------------------------------------------------------------------------

class TestInterestRate:
    def test_lump_sum(self):
        """What rate turns $1,000 into $2,000 in 10 years?"""
        result = interest_rate(pv=-1000, fv=2000, nper=10)
        assert_result_structure(result)
        expected = 2 ** (1 / 10) - 1
        assert abs(result.final_answer_value - expected) < 1e-5

    def test_annuity(self):
        """What rate makes PV = $1,000 with $100/yr payment for 15 years?"""
        result = interest_rate(pv=-1000, fv=0, nper=15, pmt=100)
        assert_result_structure(result)
        assert result.final_answer_value > 0

    def test_excel_formula_present(self):
        result = interest_rate(pv=-1000, fv=2000, nper=10)
        assert "=RATE(" in result.excel_formula


# ---------------------------------------------------------------------------
# Net Present Value
# ---------------------------------------------------------------------------

class TestNPV:
    def test_positive_npv(self):
        """NPV with positive outcome."""
        cfs = [-1000, 400, 400, 400, 400]
        result = net_present_value(rate=0.10, cash_flows=cfs)
        assert_result_structure(result)
        expected = sum(cf / 1.10 ** t for t, cf in enumerate(cfs))
        assert abs(result.final_answer_value - expected) < 0.01

    def test_negative_npv(self):
        """NPV with negative outcome at high discount rate."""
        cfs = [-1000, 200, 200, 200, 200]
        result = net_present_value(rate=0.20, cash_flows=cfs)
        assert result.final_answer_value < 0

    def test_with_explicit_investment(self):
        """NPV using separate initial_investment parameter."""
        result = net_present_value(
            rate=0.10,
            cash_flows=[400, 400, 400, 400],
            initial_investment=-1000,
        )
        cfs_combined = [-1000, 400, 400, 400, 400]
        expected = sum(cf / 1.10 ** t for t, cf in enumerate(cfs_combined))
        assert abs(result.final_answer_value - expected) < 0.01

    def test_excel_formula_present(self):
        result = net_present_value(rate=0.10, cash_flows=[-1000, 400, 400, 400, 400])
        assert "NPV(" in result.excel_formula


# ---------------------------------------------------------------------------
# Internal Rate of Return
# ---------------------------------------------------------------------------

class TestIRR:
    def test_basic_irr(self):
        """IRR for standard project cash flows."""
        cfs = [-1000, 300, 400, 500, 200]
        result = internal_rate_of_return(cash_flows=cfs)
        assert_result_structure(result)
        # Verify NPV ≈ 0 at the computed IRR
        irr = result.final_answer_value
        npv_check = sum(cf / (1 + irr) ** t for t, cf in enumerate(cfs))
        assert abs(npv_check) < 1e-4

    def test_irr_vs_npv_consistency(self):
        """IRR should be the rate that makes NPV = 0."""
        cfs = [-500, 150, 200, 250, 100]
        irr_result = internal_rate_of_return(cash_flows=cfs)
        npv_result = net_present_value(
            rate=irr_result.final_answer_value, cash_flows=cfs
        )
        assert abs(npv_result.final_answer_value) < 0.01

    def test_excel_formula_present(self):
        result = internal_rate_of_return(cash_flows=[-1000, 300, 400, 500, 200])
        assert "=IRR(" in result.excel_formula


# ---------------------------------------------------------------------------
# Bond Pricing
# ---------------------------------------------------------------------------

class TestBondPrice:
    def test_par_bond(self):
        """Bond priced at par when coupon rate = YTM."""
        result = bond_price(
            face_value=1000, coupon_rate=0.08, periods=10, ytm=0.08, frequency=2
        )
        assert_result_structure(result)
        assert abs(result.final_answer_value - 1000.0) < 0.01

    def test_discount_bond(self):
        """Bond priced below par when coupon rate < YTM."""
        result = bond_price(
            face_value=1000, coupon_rate=0.06, periods=10, ytm=0.08, frequency=2
        )
        assert result.final_answer_value < 1000

    def test_premium_bond(self):
        """Bond priced above par when coupon rate > YTM."""
        result = bond_price(
            face_value=1000, coupon_rate=0.10, periods=10, ytm=0.08, frequency=2
        )
        assert result.final_answer_value > 1000

    def test_price_formula(self):
        """Manual formula check for semi-annual bond."""
        fv, c, n, y, freq = 1000, 0.08, 10, 0.06, 2
        periodic_coupon = fv * c / freq
        periodic_ytm = y / freq
        pv_c = periodic_coupon * (1 - (1 + periodic_ytm) ** (-n)) / periodic_ytm
        pv_f = fv / (1 + periodic_ytm) ** n
        expected = pv_c + pv_f
        result = bond_price(fv, c, n, y, freq)
        assert abs(result.final_answer_value - expected) < 0.001

    def test_excel_formula_present(self):
        result = bond_price(1000, 0.08, 10, 0.08, 2)
        assert "=PV(" in result.excel_formula


# ---------------------------------------------------------------------------
# Bond YTM
# ---------------------------------------------------------------------------

class TestBondYTM:
    def test_par_bond_ytm(self):
        """YTM of par bond equals coupon rate."""
        result = bond_ytm(
            face_value=1000, coupon_rate=0.08, periods=10, price=1000.0, frequency=2
        )
        assert_result_structure(result)
        assert abs(result.final_answer_value - 0.08) < 1e-4

    def test_discount_bond_ytm_gt_coupon(self):
        """Discount bond: YTM > coupon rate."""
        result = bond_ytm(
            face_value=1000, coupon_rate=0.06, periods=10, price=864.10, frequency=2
        )
        assert result.final_answer_value > 0.06

    def test_round_trip(self):
        """Price a bond, then recover YTM from that price."""
        price_result = bond_price(1000, 0.07, 12, 0.09, 2)
        price = price_result.final_answer_value
        ytm_result = bond_ytm(1000, 0.07, 12, price, 2, guess=0.09)
        assert abs(ytm_result.final_answer_value - 0.09) < 1e-5

    def test_excel_formula_present(self):
        result = bond_ytm(1000, 0.08, 10, 1000.0, 2)
        assert "=YIELD(" in result.excel_formula


# ---------------------------------------------------------------------------
# Portfolio Statistics
# ---------------------------------------------------------------------------

class TestPortfolioStatistics:
    def test_equal_weights(self):
        """Equal-weight mean of [0.10, 0.20, 0.30] = 0.20."""
        returns = [0.10, 0.20, 0.30]
        result = portfolio_statistics(returns=returns)
        assert_result_structure(result)
        assert abs(result.final_answer_value - 0.20) < 1e-9

    def test_weighted_mean(self):
        """Weighted mean with custom weights."""
        returns = [0.05, 0.15, 0.25]
        weights = [0.5, 0.3, 0.2]
        result = portfolio_statistics(returns=returns, weights=weights)
        expected = 0.5 * 0.05 + 0.3 * 0.15 + 0.2 * 0.25
        assert abs(result.final_answer_value - expected) < 1e-9

    def test_weights_must_sum_to_one(self):
        """Weights not summing to 1.0 should raise ValueError."""
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            portfolio_statistics(returns=[0.1, 0.2], weights=[0.3, 0.3])

    def test_variance_and_std(self):
        """Variance and std dev correctly embedded in final_answer string."""
        returns = [0.10, 0.20]
        weights = [0.6, 0.4]
        result = portfolio_statistics(returns=returns, weights=weights)
        mean = 0.6 * 0.10 + 0.4 * 0.20
        var = 0.6 * (0.10 - mean) ** 2 + 0.4 * (0.20 - mean) ** 2
        std = math.sqrt(var)
        assert f"{std:.6f}" in result.final_answer

    def test_excel_formula_present(self):
        result = portfolio_statistics(returns=[0.1, 0.2, 0.3])
        assert "SUMPRODUCT" in result.excel_formula


# ---------------------------------------------------------------------------
# CAPM
# ---------------------------------------------------------------------------

class TestCAPM:
    def test_basic_capm(self):
        """CAPM: Rf=3%, β=1.2, Rm=10% → E(R) = 3% + 1.2×7% = 11.4%."""
        result = capm_expected_return(
            risk_free_rate=0.03, beta=1.2, market_return=0.10
        )
        assert_result_structure(result)
        assert abs(result.final_answer_value - 0.114) < 1e-9

    def test_beta_one(self):
        """When β=1, expected return equals market return."""
        result = capm_expected_return(
            risk_free_rate=0.03, beta=1.0, market_return=0.10
        )
        assert abs(result.final_answer_value - 0.10) < 1e-9

    def test_beta_zero(self):
        """When β=0, expected return equals risk-free rate."""
        result = capm_expected_return(
            risk_free_rate=0.03, beta=0.0, market_return=0.10
        )
        assert abs(result.final_answer_value - 0.03) < 1e-9

    def test_excel_formula_present(self):
        result = capm_expected_return(0.03, 1.2, 0.10)
        assert "+" in result.excel_formula and "*" in result.excel_formula


# ---------------------------------------------------------------------------
# Straight-Line Depreciation
# ---------------------------------------------------------------------------

class TestStraightLineDepreciation:
    def test_basic(self):
        """SLN: Cost=$10,000, Salvage=$2,000, Life=8 years → $1,000/yr."""
        result = straight_line_depreciation(10000, 2000, 8)
        assert_result_structure(result)
        assert abs(result.final_answer_value - 1000.0) < 1e-9

    def test_zero_salvage(self):
        result = straight_line_depreciation(5000, 0, 5)
        assert abs(result.final_answer_value - 1000.0) < 1e-9

    def test_book_value_reaches_salvage(self):
        """Book value at end of life must equal salvage value."""
        cost, salvage, life = 10000, 1000, 9
        result = straight_line_depreciation(cost, salvage, life)
        book_value_end = cost - result.final_answer_value * life
        assert abs(book_value_end - salvage) < 1e-6

    def test_excel_formula_present(self):
        result = straight_line_depreciation(10000, 2000, 8)
        assert "=SLN(" in result.excel_formula


# ---------------------------------------------------------------------------
# Payback Period
# ---------------------------------------------------------------------------

class TestPaybackPeriod:
    def test_exact_recovery(self):
        """Payback when CFs exactly equal investment in integer periods."""
        result = payback_period(1000, [500, 500, 200])
        assert_result_structure(result)
        assert abs(result.final_answer_value - 2.0) < 1e-9

    def test_fractional_payback(self):
        """Fractional payback period."""
        result = payback_period(1000, [400, 400, 400, 400])
        assert abs(result.final_answer_value - 2.5) < 1e-9

    def test_no_recovery(self):
        """Project does not recover investment."""
        result = payback_period(1000, [100, 100, 100])
        assert result.final_answer_value is None
        assert "Not recovered" in result.final_answer

    def test_first_period_recovery(self):
        """Payback within first period."""
        result = payback_period(500, [1000, 200])
        assert abs(result.final_answer_value - 0.5) < 1e-9

    def test_assumptions_present(self):
        """Assumptions should be populated for payback."""
        result = payback_period(1000, [500, 500])
        assert len(result.assumptions) >= 1


# ---------------------------------------------------------------------------
# SolverResult str output
# ---------------------------------------------------------------------------

class TestSolverResultStr:
    def test_str_contains_all_sections(self):
        result = future_value(pv=1000, rate=0.05, nper=10)
        output = str(result)
        for marker in [
            "[1] QUESTION",
            "[2] INPUTS",
            "[3] FORMULA",
            "[4] STEP-BY-STEP",
            "[5] EXCEL FORMULA",
            "[6] CROSS-CHECK",
            "[7] SANITY CHECK",
            "FINAL ANSWER:",
        ]:
            assert marker in output, f"Missing section: {marker}"

    def test_assumptions_section_shown_when_present(self):
        result = payback_period(1000, [400, 400, 400])
        output = str(result)
        assert "[*] ASSUMPTIONS" in output
