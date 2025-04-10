import pytest

from pybikes import BikeShareStation, BikeShareSystem
from pybikes.base import Vehicle, VehicleType, VehicleTypes

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


class TestVehicle:
    @pytest.fixture()
    def system_a(self):
        return BikeShareSystem('foo', {
            'name': "foo",
        })

    @pytest.fixture()
    def system_b(self):
        return BikeShareSystem('bar', {
            'name': "bar",
        })

    @pytest.fixture()
    def vehicles(self, system_a, system_b):
        return [
            # same latlng, different uid, same system, different hash
            Vehicle(0.0, 0.0, extra={'uid': 'abc'}, system=system_a),
            Vehicle(0.0, 0.0, extra={'uid': 'def'}, system=system_a),
            # different latlng, same uid, same system, same hash
            Vehicle(1.0, 2.0, extra={'uid': 'abc'}, system=system_a),
            Vehicle(0.0, 0.0, extra={'uid': 'abc'}, system=system_a),
            # same latlng, same uid, different system, different hash
            Vehicle(0.0, 0.0, extra={'uid': 'abc'}, system=system_a),
            Vehicle(0.0, 0.0, extra={'uid': 'abc'}, system=system_b),
            # different latlng, no uid, same system, different hash
            Vehicle(1.0, 2.0, extra={}, system=system_a),
            Vehicle(0.0, 0.0, extra={}, system=system_a),
            # same latlng, no uid, same system, different kind, diff hash
            Vehicle(0.0, 0.0, extra={}, vehicle_type=VehicleTypes.bicycle, system=system_a),
            Vehicle(0.0, 0.0, extra={}, vehicle_type=VehicleTypes.ebike, system=system_a),
            # same latlng, no uid, same system, same hash (shrug)
            Vehicle(0.0, 0.0, extra={}, system=system_a),
            Vehicle(0.0, 0.0, extra={}, system=system_a),
            # same latlng, no uid, different system, different hash
            Vehicle(0.0, 0.0, extra={}, system=system_a),
            Vehicle(0.0, 0.0, extra={}, system=system_b),
        ]

    def test_hash(self, vehicles):
        assert [v.hash for v in vehicles] == [
            '9777d27aaac930a2f142b0081e6f5f19',
            'e6bad737df8183d17b5d0f1adbf6da78',

            '9777d27aaac930a2f142b0081e6f5f19',
            '9777d27aaac930a2f142b0081e6f5f19',

            '9777d27aaac930a2f142b0081e6f5f19',
            '253f3787587d71762c198cf35ecc2306',

            '1174c1f45ba6631f774de058be886a5e',
            'cb95809a7c2ab6d696430fb44d773a7e',

            'cb95809a7c2ab6d696430fb44d773a7e',
            '59ffa508d2a05f3a2465e9c5961124b9',

            'cb95809a7c2ab6d696430fb44d773a7e',
            'cb95809a7c2ab6d696430fb44d773a7e',

            'cb95809a7c2ab6d696430fb44d773a7e',
            '70d51ca6744b120475e295477b8c1377',
        ]

    def test_system_introspection(self):
        class MockSystem(BikeShareSystem):
            meta = {'name': 'Foo'}

            def update(self, * args, ** kwargs):
                self.vehicles = [
                    Vehicle(0.0, 0.0, extra={}),
                ]

                assert self.vehicles[0].system == self

        system = MockSystem('foo', {})
        system.update()

    def test_vehicle_type_kind(self):
        assert Vehicle(0.0, 0.0).kind == VehicleTypes.default
        assert Vehicle(0.0, 0.0).to_dict()['kind'] == VehicleTypes.default.alias

        vt = VehicleType(power="mock", name="Mock Vehicle", alias="mock")
        assert Vehicle(0.0, 0.0, vehicle_type=vt).kind == vt
        assert Vehicle(0.0, 0.0, vehicle_type=vt).to_dict()['kind'] == vt.alias


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
