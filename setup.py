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
        'pybikes': ['data/*.json', 'kml/*.kml', 'kml/*.kml.gz'],
    },
    license="LICENSE.txt",
    description="A python library for scrapping bike sharing data",
    long_description=open('README.md').read(),
    install_requires=[
        'requests>=2.20.0',
        'lxml',
        'cssselect>=0.9',
        'shapely>=1.5.13',
    ],
)
