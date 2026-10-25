import subprocess

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "update: mark a test that uses network and might fail"
    )


def pytest_addoption(parser):
    parser.addoption(
        "--diff", metavar="REF", help="only run instance tests changed since REF"
    )


def pytest_collection_modifyitems(config, items):
    instance_diff(config.getoption("--diff"), config, items)


def instance_diff(ref, config, items):
    """deselect all test items that have not changed since ref"""
    # nop
    if not ref:
        return

    from tests.changes import select_items

    selected, deselected = select_items(items, ref, "HEAD")
    config.hook.pytest_deselected(items=deselected)
    items[:] = selected
