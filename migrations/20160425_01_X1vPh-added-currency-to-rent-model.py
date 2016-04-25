"""
Added currency to Rent model
"""

from yoyo import step

__depends__ = {'20160411_01_ylLTx-added-iphash-and-createdat-to-rent-model'}

steps = [
    step("ALTER TABLE rent ADD currency VARCHAR(3) NOT NULL DEFAULT 'EUR'"),
]
