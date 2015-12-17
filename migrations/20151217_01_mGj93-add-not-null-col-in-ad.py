"""
Add not-null col in Ad
"""

from yoyo import step

__depends__ = {'20151208_02_dPGPe-rename-currencys-col-in-ad'}

steps = [
    step("ALTER TABLE ad CHANGE COLUMN site site VARCHAR(30) NOT NULL"),
    step("DELETE FROM ad WHERE site_id is NULL"),
    step("ALTER TABLE ad CHANGE COLUMN site_id site_id VARCHAR(100) NOT NULL"),
    step("ALTER TABLE ad CHANGE COLUMN country country VARCHAR(2) NOT NULL"),
]
