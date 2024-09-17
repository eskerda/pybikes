""" Very hacky script that runs tests on bike share systems that have
changed on a specific branch. Checks for changes on data files and
classes containing bike share systems.

This is meant for red explicit fails on changes in CI
"""

import re
import os
import git
import inspect

from pytest import mark
from warnings import warn

from pybikes import BikeShareSystem
from pybikes.data import get_instances
from pybikes.compat import resources

from tests.test_instances import get_test_cls


def is_system(mod, obj):
    if not inspect.isclass(obj):
        return False

    # Only declared in module
    if obj.__module__ != mod.__name__:
        return False

    if not issubclass(obj, BikeShareSystem):
        return False

    if obj == BikeShareSystem:
        return False

    return True


def generate_tests_from_changes(branch):

    # this will fail in python < 3.8
    from importlib.util import spec_from_file_location, module_from_spec

    # this might fail if branch not in git dir
    g = git.cmd.Git(os.getcwd())
    changed_files = g.diff('--name-only', branch).splitlines()
    clss = set()

    for file in changed_files:
        if re.match(r'pybikes/data/.*\.json', file):
            # Extract classes from json file
            match = re.search(r'pybikes/data/(.*)\.json', file)
            schema = match.group(1)
            [clss.add(cls) for cls, _ in get_instances(schema)]
        elif re.match(r'pybikes/.*\.py', file):
            # Extract bike share classes from file
            spec = spec_from_file_location('some.mod', file)
            mod = module_from_spec(spec)
            spec.loader.exec_module(mod)
            systems = filter(lambda m: is_system(mod, m[1]), inspect.getmembers(mod))
            [clss.add(cls) for cls, _ in systems]

    for cls in sorted(clss):
        test_cls = get_test_cls(cls)
        # decorate with pytest mark 'changes'
        test_cls = mark.changes(test_cls)
        globals()[test_cls.__name__] = test_cls


# non-optimal not-required
try:
    generate_tests_from_changes('origin/master')
except Exception as e:
    warn("Failed generating tests from branch changes: " + str(e))

# Force pytest to succeed when no tests are marked with 'changes'
@mark.changes
def test_dummy():
    assert True
