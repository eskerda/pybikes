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