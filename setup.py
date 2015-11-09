#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of rentswatch-scraper.
# https://github.com/jplusplus/rentswatch-scraper

# Licensed under the LGPL license:
# http://www.opensource.org/licenses/LGPL-license
# Copyright (c) 2015, pirhoo <hello@pirhoo.com>

from setuptools import setup, find_packages
from rentswatch_scraper import __version__

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='rentswatch-scraper',
    version=__version__,
    description='A basic framework to scrap renting ads',
    long_description=readme(),
    keywords='',
    author='pirhoo',
    author_email='hello@pirhoo.com',
    url='https://github.com/jplusplus/rentswatch-scraper',
    license='LGPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'SQLObject==2.1.2',
        'beautifulsoup4==4.4.0',
        'requests==2.2.1',
        'MySQL-python==1.2.3'
    ],
    extras_require={
        'tests': [],
    },
    entry_points={
        'console_scripts': [
            # add cli scripts here in this form:
            # 'rentswatch-scraper=rentswatch_scraper.cli:main',
        ],
    },
)
