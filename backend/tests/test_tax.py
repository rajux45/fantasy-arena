from __future__ import annotations

from app.services.tax_service import (
    compute_gst_on_entry,
    compute_tds_on_withdrawal,
    split_gst_inclusive,
)


def test_split_gst_inclusive_28pct() -> None:
    # ₹100 inclusive of 28% GST -> ₹78.13 net + ₹21.87 GST  (paise: 7813 + 2187 = 10000)
    net, gst = split_gst_inclusive(10_000)
    assert net + gst == 10_000
    assert 2_180 <= gst <= 2_195


def test_compute_gst_on_entry() -> None:
    assert compute_gst_on_entry(0) == 0
    assert 105 <= compute_gst_on_entry(490) <= 110  # ₹4.90 entry, GST ≈ ₹1.07


def test_tds_no_net_winnings() -> None:
    tds, payout = compute_tds_on_withdrawal(
        requested_paise=50_000,
        cumulative_winnings_paise=10_000,
        cumulative_deposits_paise=20_000,
        tds_already_paid_paise=0,
    )
    assert tds == 0
    assert payout == 50_000


def test_tds_with_net_winnings() -> None:
    tds, payout = compute_tds_on_withdrawal(
        requested_paise=50_000,
        cumulative_winnings_paise=1_00_000,
        cumulative_deposits_paise=20_000,
        tds_already_paid_paise=0,
    )
    # Net winnings = 80_000, expected TDS = 30% = 24_000
    assert tds == 24_000
    assert payout == 26_000


def test_tds_credit_for_already_paid() -> None:
    tds, payout = compute_tds_on_withdrawal(
        requested_paise=50_000,
        cumulative_winnings_paise=1_00_000,
        cumulative_deposits_paise=20_000,
        tds_already_paid_paise=20_000,
    )
    # Expected new TDS = 24_000 - 20_000 = 4_000
    assert tds == 4_000
    assert payout == 46_000
