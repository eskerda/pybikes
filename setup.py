# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from setuptools import setup, find_packages

setup(
    name = "PyBikes",
    version = "0.2dev",
    author = "Lluis Esquerda",
    author_email = "eskerda@gmail.com",
    packages = ["pybikes", "pybikes.test"],
    package_data = {
        'pybikes': ['data/*.json'],
    },
    license = "LICENSE.txt",
    description = "A python library for scrapping bike sharing data",
    long_description = open('README.txt').read(),
    install_requires = ['pyquery','requests'],
)