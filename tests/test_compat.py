import pybikes

from pybikes.data import get_all_data, get_schemas, get_system_cls
from pybikes.data import get_instance

from pybikes.data import find
from pybikes.emovity import Emovity


def test_get_all_data():
    assert get_all_data()


def test_get_schemas():
    assert len(get_all_data()) == len(get_schemas())


def test_get_system_cls():
    assert get_system_cls('emovity', 'Emovity') == Emovity


def test_get_instance():
    mod_name, cls_name, i_data = find('girocleta')
    assert get_instance('emovity', 'girocleta') == (cls_name, i_data)
