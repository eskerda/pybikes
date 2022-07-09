import pytest

from pybikes import BikeShareStation, BikeShareSystem

class TestBikeShareStation:

    @pytest.fixture()
    def stations(self):
        return [
            BikeShareStation('foo', 40.0149856, -105.2705455, 10, 20, {'foo': 'fuzz'}),
            BikeShareStation('bar', 19.4326077, -99.13320799999997, 10, 20, {'bar': 'baz'}),
        ]

    def test_hash(self, stations):
        assert [s.get_hash() for s in stations] == [
            "e1aea428a04db6a77c4a1a091edcfcb6",
            "065d7bb95e6c9079190334ee0d320c72",
        ]

class TestBikeShareSystem:

    @pytest.fixture()
    def systems(self):
        metaFoo = {
            'name': 'Foo',
            'uname': 'foo',
            'city': 'Fooland',
            'country': 'FooEmpire',
            'latitude': 10.12312,
            'longitude': 1.12312,
            'company': ['FooCompany']
        }

        metaBar = {
            'name': 'Bar',
            'uname': 'bar',
            'city': 'Barland',
            'population': 100000
        }

        class FooSystem(BikeShareSystem):
            pass

        class BarSystem(BikeShareSystem):
            meta = {
                'company': ['BarCompany']
            }

        return {
            "foo": FooSystem('foo', metaFoo),
            "bar": BarSystem('bar', metaBar),
        }

    def test_tag(self, systems):
        assert systems['foo'].tag == "foo"
        assert systems['bar'].tag == "bar"

    def test_base_meta_always_set(self, systems):
        for meta in BikeShareSystem.meta:
            assert meta in systems['foo'].meta
            assert meta in systems['bar'].meta

    def test_meta_composes(self, systems):
        assert systems['foo'].meta == {
            'name': 'Foo',
            'uname': 'foo',
            'city': 'Fooland',
            'country': 'FooEmpire',
            'latitude': 10.12312,
            'longitude': 1.12312,
            'company': ['FooCompany']
        }

        assert systems['bar'].meta == {
            'name': 'Bar',
            'uname': 'bar',
            'city': 'Barland',
            'population': 100000,
            'company': ['BarCompany'],
            'country': None,
            'latitude': None,
            'longitude': None,
        }
