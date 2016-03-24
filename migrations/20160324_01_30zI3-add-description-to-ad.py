"""
Add description to Ad
"""

from yoyo import step

__depends__ = {'20151217_01_mGj93-add-not-null-col-in-ad'}

steps = [
    step("ALTER TABLE ad ADD description TEXT DEFAULT ''"),
]
