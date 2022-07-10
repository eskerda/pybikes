import pytest

try:
    # python 3
    from unittest.mock import patch, Mock
except ImportError:
    # python 2
    from mock import patch, Mock

from pybikes.data import find, get, _traverse_lib
from pybikes.exceptions import BikeShareSystemNotFound


class foobar:
    class Foobar(Mock):
        authed = False


class barbaz:
    class BarBaz(Mock):
        authed = False


    class BazBar(Mock):
        authed = False

    class BazBarPremium(Mock):
        authed = True


mock_classes = {
    'pybikes.foobar': foobar(),
    'pybikes.barbaz': barbaz(),
}

foobar_data = {
    "system": "foobar",
    "class": "Foobar",
    "instances": [
        {"tag": "foobar-rocks", "meta": {"foo": "bar"}},
        {"tag": "foobar-sucks", "meta": {"foo": "bar"}},
    ],
}

barbaz_data = {
    "system": "barbaz",
    "class": {
        "BarBaz": {
            "instances": [
                {"tag": "barbaz-rocks", "meta": {"foo": "bar"}},
                {"tag": "barbaz-sucks", "meta": {"foo": "bar"}},
            ],
        },
        "BazBar": {
            "instances": [
                {"tag": "bazbar-rocks", "meta": {"foo": "bar"}},
                {"tag": "bazbar-sucks", "meta": {"foo": "bar"}},
            ],
        },
        "BazBarPremium": {
            "instances": [
                {"tag": "bazbar-summer"},
            ],
        },
    },
}

mock_data = [
    ('foobar.json', foobar_data),
    ('barbaz.json', barbaz_data),
]


def _import(name):
    return mock_classes[name]


def _iter_data():
    return iter(mock_data)


@patch('pybikes.data._import', _import)
@patch('pybikes.data._iter_data', _iter_data)
@patch('pybikes.data._t_cache', {})
@patch('pybikes.data._traversor', _traverse_lib())
class TestData:
    def test_find_not_found(self):
        with pytest.raises(BikeShareSystemNotFound):
            find("abracadabra")


    def test_find_single_class(self):
        mod, cls, i_data = find('foobar-rocks')
        assert mod == "foobar"
        assert cls == "Foobar"
        assert i_data == foobar_data['instances'][0]


    def test_find_multi_class(self):
        mod, cls, i_data = find('bazbar-sucks')
        assert mod == "barbaz"
        assert cls == "BazBar"
        assert i_data == barbaz_data['class']['BazBar']['instances'][1]


    def test_get_not_found(self):
        with pytest.raises(BikeShareSystemNotFound):
            get("abracadabra")


    def test_get_instances(self):
        assert isinstance(get("foobar-rocks"), foobar.Foobar)
        assert isinstance(get("foobar-sucks"), foobar.Foobar)

        assert isinstance(get("barbaz-rocks"), barbaz.BarBaz)
        assert isinstance(get("barbaz-sucks"), barbaz.BarBaz)

        assert isinstance(get("bazbar-rocks"), barbaz.BazBar)
        assert isinstance(get("bazbar-sucks"), barbaz.BazBar)


    def test_get_instance_needs_key(self):
        foo = get("bazbar-summer", key="foobar")
        assert getattr(foo, 'key') == "foobar"


    def test_get_instance_needs_key_error(self):
        with pytest.raises(Exception):
            get("bazbar-summer")
