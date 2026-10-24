import copy
import json

import git
import pytest

from pybikes.data import _datafile_traversor
from tests import test_changes
from tests.test_instances import classes, get_test_cls


@pytest.fixture
def changed_catalog(tmp_path, monkeypatch):
    data = {
        'system': 'example',
        'class': 'Example',
        'instances': [
            {'tag': 'one', 'endpoint': 'https://one.example'},
            {'tag': 'two', 'endpoint': 'https://two.example'},
        ],
    }
    path = tmp_path / 'pybikes/data/example.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(data))
    repository = git.Repo.init(tmp_path)
    repository.index.add(['pybikes/data/example.json'])
    actor = git.Actor('the8thbit', 'the8thbit@users.noreply.github.com')
    base = repository.index.commit('Initial catalog', author=actor, committer=actor).hexsha
    selected = {}

    def capture(cls, tags=None):
        selected[cls] = tags
        return type('Selected' + cls, (), {})

    def local_instances(schema):
        catalog = json.loads((tmp_path / 'pybikes/data' / (schema + '.json')).read_text())
        yield from _datafile_traversor(catalog['class'], catalog.get('instances', []))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(test_changes, 'get_test_cls', capture)
    monkeypatch.setattr(test_changes, 'get_instances', local_instances, raising=False)
    return path, data, base, selected


def test_json_edit_selects_only_changed_instance(changed_catalog):
    path, data, base, selected = changed_catalog
    data['instances'][1]['endpoint'] = 'https://new.example'
    path.write_text(json.dumps(data))
    test_changes.generate_tests_from_changes(base)
    assert selected == {'Example': {'two'}}


def test_reordering_and_removed_instances_need_no_live_checks(changed_catalog):
    path, data, base, selected = changed_catalog
    data['instances'] = list(reversed(data['instances']))
    path.write_text(json.dumps(data))
    test_changes.generate_tests_from_changes(base)
    assert selected == {}
    data['instances'].pop()
    path.write_text(json.dumps(data))
    test_changes.generate_tests_from_changes(base)
    assert selected == {}


def test_new_catalog_selects_all_its_instances(changed_catalog):
    path, data, base, selected = changed_catalog
    new_data = copy.deepcopy(data)
    new_data['class'] = 'NewExample'
    new_data['instances'] = [{'tag': 'new'}]
    path.with_name('new.json').write_text(json.dumps(new_data))
    repository = git.Repo(path.parents[2])
    repository.index.add(['pybikes/data/new.json'])
    test_changes.generate_tests_from_changes(base)
    assert selected == {'NewExample': {'new'}}


def test_multiclass_catalog_selects_new_or_changed_tags(changed_catalog):
    path, data, base, selected = changed_catalog
    data['class'] = {
        'Example': {'instances': data.pop('instances')},
        'OtherExample': {'instances': [{'tag': 'three'}]},
    }
    data['class']['Example']['instances'][0]['endpoint'] = 'https://new.example'
    path.write_text(json.dumps(data))
    test_changes.generate_tests_from_changes(base)
    assert selected == {'Example': {'one'}, 'OtherExample': {'three'}}


def test_python_change_keeps_whole_class_checks(changed_catalog):
    path, data, base, selected = changed_catalog
    data['instances'][1]['endpoint'] = 'https://new.example'
    path.write_text(json.dumps(data))
    module = path.parents[1] / 'example.py'
    module.write_text(
        'from pybikes import BikeShareSystem\n'
        'class Example(BikeShareSystem):\n    pass\n'
    )
    repository = git.Repo(path.parents[2])
    repository.index.add(['pybikes/example.py'])
    test_changes.generate_tests_from_changes(base)
    assert selected == {'Example': None}


def test_deleted_catalog_is_ignored(changed_catalog):
    path, _, base, selected = changed_catalog
    path.unlink()
    test_changes.generate_tests_from_changes(base)
    assert selected == {}


def test_system_module_change_checks_each_instance(changed_catalog):
    path, data, base, selected = changed_catalog
    data['system'] = 'replacement'
    path.write_text(json.dumps(data))
    test_changes.generate_tests_from_changes(base)
    assert selected == {'Example': {'one', 'two'}}


def test_instance_test_class_filters_tags():
    cls = next(name for name, instances in classes.items() if len(instances) > 1)
    tag = classes[cls][0][1]['tag']
    filtered = get_test_cls(cls, tags={tag})
    marker = next(m for m in filtered.pytestmark if m.name == 'parametrize')
    assert [instance_data[1]['tag'] for instance_data in marker.args[1]] == [tag]
