#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of rentswatch-scraper.
# https://github.com/jplusplus/rentswatch-scraper

# Licensed under the LGPL license:
# http://www.opensource.org/licenses/LGPL-license
# Copyright (c) 2015, pirhoo <hello@pirhoo.com>

from setuptools import setup, find_packages
from rentswatch_scraper import __version__

tests_require = [
    'mock',
    'nose',
    'coverage',
    'yanc',
    'preggy',
    'tox',
    'ipdb',
    'coveralls',
    'sphinx',
]

setup(
    name='rentswatch-scraper',
    version=__version__,
    description='an incredible python package',
    long_description='''
an incredible python package
''',
    keywords='',
    author='pirhoo',
    author_email='hello@pirhoo.com',
    url='https://github.com/jplusplus/rentswatch-scraper',
    license='LGPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: LGPL License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=False,
    install_requires=[
        # add your dependencies here
        # remember to use 'package-name>=x.y.z,<x.y+1.0' notation (this way you get bugfixes)
    ],
    extras_require={
        'tests': tests_require,
    },
    entry_points={
        'console_scripts': [
            # add cli scripts here in this form:
            # 'rentswatch-scraper=rentswatch_scraper.cli:main',
        ],
    },
)
