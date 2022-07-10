import pybikes

from pybikes.compat import get_all_data, get_schemas, get_system_cls
from pybikes.compat import get_instance

from pybikes.data import find
from pybikes.bicing import Bicing


def test_get_all_data():
    assert get_all_data()


def test_get_schemas():
    assert len(get_all_data()) == len(get_schemas())


def test_get_system_cls():
    assert get_system_cls('bicing', 'Bicing') == Bicing


def test_get_instance():
    mod_name, cls_name, i_data = find('bicing')
    assert get_instance('bicing', 'bicing') == (cls_name, i_data)
