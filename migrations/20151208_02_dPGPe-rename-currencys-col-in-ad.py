"""
Rename currency's col in Ad
"""

from yoyo import step

__depends__ = {'20151208_01_a2Dh8-add-currency-to-ad'}

steps = [
    step("ALTER TABLE ad RENAME serviceChargeOriginalCurrency TO service_charge_original_currency"),
    step("ALTER TABLE ad RENAME baseRentOriginalCurrency TO ba_serent_original_currency"),
    step("ALTER TABLE ad RENAME totalRentOriginalCurrency TO tot_alrent_original_currency"),
]
