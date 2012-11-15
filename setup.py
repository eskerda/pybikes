# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from setuptools import setup, find_packages

setup(
    name = "PyBikes",
    version = "0.2dev",
    packages = "pybikes",
    install_requires = ['pyquery'],
    package_data = {
        'pybikes': ['data/*.json'],
    }
)