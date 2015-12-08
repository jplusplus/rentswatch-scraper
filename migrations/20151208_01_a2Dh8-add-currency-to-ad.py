"""
Add currency to Ad
"""

from yoyo import step

__depends__ = {}

steps = [
    step("ALTER TABLE ad ADD serviceChargeOriginalCurrency FLOAT NULL"),
    step("ALTER TABLE ad ADD baseRentOriginalCurrency FLOAT NULL"),
    step("ALTER TABLE ad ADD totalRentOriginalCurrency FLOAT NULL"),
    step("ALTER TABLE ad ADD currency VARCHAR(3) DEFAULT 'EUR'"),
]
