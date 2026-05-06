"""GST (Sec 9) and TDS (Sec 194BA) calculators.

All amounts are in **paise** (integer). Functions are pure — no DB calls.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

GST_RATE = Decimal("0.28")  # 28%
TDS_RATE = Decimal("0.30")  # 30%


def _round(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def split_gst_inclusive(gross_paise: int) -> tuple[int, int]:
    """Given a gross deposit `gross_paise` that is GST-inclusive, return (net_credit, gst).

    Formula (28% inclusive): gst = gross * 28/128.
    """
    gross = Decimal(gross_paise)
    gst = gross * GST_RATE / (Decimal(1) + GST_RATE)
    gst_int = _round(gst)
    return gross_paise - gst_int, gst_int


def compute_gst_on_entry(entry_fee_paise: int) -> int:
    """Inclusive GST on a contest entry-fee equivalent payment."""
    _, gst = split_gst_inclusive(entry_fee_paise)
    return gst


def compute_tds_on_withdrawal(
    *,
    requested_paise: int,
    cumulative_winnings_paise: int,
    cumulative_deposits_paise: int,
    tds_already_paid_paise: int,
) -> tuple[int, int]:
    """Return (tds_to_deduct, payout_amount).

    Per Section 194BA, TDS = 30% of net winnings at the time of withdrawal,
    where net winnings = (winnings - deposits used) since FY start, less prior TDS.
    """
    net_winnings = Decimal(cumulative_winnings_paise) - Decimal(cumulative_deposits_paise)
    if net_winnings <= 0:
        return 0, requested_paise

    expected_tds = (net_winnings * TDS_RATE).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    tds_due = max(Decimal(0), expected_tds - Decimal(tds_already_paid_paise))
    tds_due_int = min(_round(tds_due), requested_paise)
    return tds_due_int, requested_paise - tds_due_int
