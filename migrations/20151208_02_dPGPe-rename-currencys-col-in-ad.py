"""
Rename currency's col in Ad
"""

from yoyo import step

__depends__ = {'20151208_01_a2Dh8-add-currency-to-ad'}

steps = [
    step("ALTER TABLE ad CHANGE COLUMN serviceChargeOriginalCurrency service_charge_original_currency FLOAT"),
    step("ALTER TABLE ad CHANGE COLUMN baseRentOriginalCurrency base_rent_original_currency FLOAT"),
    step("ALTER TABLE ad CHANGE COLUMN totalRentOriginalCurrency total_rent_original_currency FLOAT"),
]
