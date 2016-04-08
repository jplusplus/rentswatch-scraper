"""
Added Rent model
"""

from yoyo import step

__depends__ = {'20160324_01_30zI3-add-description-to-ad'}

steps = [
    step("""CREATE TABLE rent (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        total_rent FLOAT,
        living_space FLOAT,
        address VARCHAR(1000)
    )""")
]
