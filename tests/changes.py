import os
import re
import ast
import json
from pathlib import Path

import git

from pybikes.data import _datafile_traversor


def diff(a, b):
    """compare to data files for changes"""
    a = _datafile_traversor(a.get("class"), a.get("instances", []))
    b = _datafile_traversor(b.get("class"), b.get("instances", []))

    a_i = {(cls, i["tag"]): i for cls, i in a}
    b_i = {(cls, i["tag"]): i for cls, i in b}

    for key, instance in a_i.items():
        if instance == b_i.get(key):
            continue
        yield instance


def get_diff(ref_a, ref_b):
    """compare two git refs to extract whole classes and instances that changed"""
    g = git.cmd.Git(os.getcwd())

    base = g.merge_base(ref_a, ref_b)
    files = g.diff("--name-only", "--diff-filter=d", base).splitlines()

    tags = set()
    clss = set()

    for file in files:
        if re.match(r"pybikes/data/.*\.json$", file):
            current = json.loads(Path(file).read_text())
            try:
                prev = json.loads(g.show("%s:%s" % (base, file)))
                changed = diff(current, prev)
            except (git.exc.GitCommandError, json.JSONDecodeError):
                # prev refspec does not exist, or is not valid json
                changed = diff(current, {})

            tags.update((i["tag"] for i in changed))

        elif re.match(r"pybikes/.*\.py$", file):
            tree = ast.parse(Path(file).read_text())
            mod_clss = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
            clss.update(mod_clss)

    return tags, clss
