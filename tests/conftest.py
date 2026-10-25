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

    from tests.changes import get_diff

    tags, clss = get_diff(ref, "HEAD")

    def include(item):
        params = getattr(getattr(item, "callspec", None), "params", {})
        tag = getattr(params.get("instance"), "tag", None)
        cls = params.get("cls")
        return bool(tag and cls and (cls in clss or tag in tags))

    selected = [i for i in items if include(i)]
    deselected = [i for i in items if not include(i)]

    config.hook.pytest_deselected(items=deselected)
    items[:] = selected
