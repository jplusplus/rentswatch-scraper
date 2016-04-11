"""
Added ipHash and createdAt to Rent model
"""

from yoyo import step

__depends__ = {'20160408_02_wg1lz-added-movein-to-rent-model'}

steps = [
    step("ALTER TABLE rent ADD created_at TIMESTAMP NOT NULL DEFAULT now()"),
    step("ALTER TABLE rent ADD ip_hash VARCHAR(512) NOT NULL DEFAULT ''"),
]
