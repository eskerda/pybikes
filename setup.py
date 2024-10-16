# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from setuptools import setup

setup(
    name="pybikes",
    version="1.0",
    author="Lluis Esquerda",
    author_email="eskerda@gmail.com",
    packages=["pybikes"],
    package_data={
        'pybikes': ['data/*.json', 'geojson/*.json'],
    },
    license="LICENSE.txt",
    description="A python library for scrapping bike sharing data",
    long_description=open('README.md').read(),
    install_requires=[
        'requests>=2.20.0',
        'lxml',
        'shapely>=1.5.13',
        'future',
        "importlib_resources; python_version < '3.9'",
        'cssselect'
    ],
)
