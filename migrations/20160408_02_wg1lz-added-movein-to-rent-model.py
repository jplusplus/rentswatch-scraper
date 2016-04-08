"""
Added moveIn to Rent model
"""

from yoyo import step

__depends__ = {'20160408_01_OgXf5-added-rent-model'}

steps = [
    step("ALTER TABLE rent ADD move_in DATE"),
]
