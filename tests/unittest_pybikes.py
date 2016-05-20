# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt
import re
import unittest
import sys

import pybikes
import keys


class TestSystems(unittest.TestCase):
    def _test_systems(self, schema):
        key = getattr(keys, schema, None)
        print('\nTesting %s' % schema)
        print('=============================')
        for cname, instance in pybikes.get_instances(schema):
            self._test_system(instance['tag'], key)

    def _test_system(self, tag, key=None):
        """ Tests okayness of a system:
            - Test if system can be updated
            - Tests okayness of 5 stations on the system
        """
        p_sys = pybikes.get(tag, key)
        print(u'Testing {!r}, {!r}'.format(p_sys.meta['name'], p_sys.meta.get('city')))
        self._test_update(p_sys)
        station_string = ""
        if len(p_sys.stations) < 5:
            t_range = len(p_sys.stations)
        else:
            t_range = 5
        for i in range(t_range):
            station_string += unichr(ord(u'▚') + i)
            sys.stdout.flush()
            sys.stdout.write('\r[%s] testing %d' % (station_string, i+1))
            sys.stdout.flush()
            self._test_station_ok(p_sys, p_sys.stations[i])
        sys.stdout.flush()
        sys.stdout.write('\r↑ stations look ok ↑                          \n\n')
        sys.stdout.flush()

    def _test_station_ok(self, instance, station):
        """ Tests okayness of a station:
            - coming from an async system
                - Station can be updated
            - Station has its base parameters
        """
        if not instance.sync:
            station.update()
            self._test_allows_parameter(station)
        else:
            self._test_dumb_allows_parameter(station)
        # Required fields
        self.assertIsNotNone(station.bikes)
        self.assertIsNotNone(station.latitude)
        self.assertIsNotNone(station.longitude)
        self.assertIsNotNone(station.name)

        # Type checking
        self.assertIsInstance(station.bikes, int)
        self.assertIsInstance(station.latitude, float)
        self.assertIsInstance(station.longitude, float)
        if station.free:
            self.assertIsInstance(station.free, int)

    def _test_update(self, instance):
        """ Tests if this system can be updated
            we assume that having more than 0 stations
            means being updateable. Also, test if its update function
            allows a PyBikesScraper parameter
        """
        instance.update()
        print("%s has %d stations" % (
            instance.meta['name'], len(instance.stations)
        ))
        self.assertTrue(len(instance.stations) > 0)
        self._test_allows_parameter(instance)

    def _test_allows_parameter(self, instance):
        """ Tests if this instance, be it a system or a station, allows a
            PyBikesScraper parameter for its update method
        """
        scraper = pybikes.utils.PyBikesScraper()
        instance.update(scraper)
        self.assertIsNotNone(scraper.last_request)

    def _test_dumb_allows_parameter(self, instance):
        """ Dumber version of the allows parameter test, in this case, we
            just want to check that calling a synchronous system station
            update with an scraper does not fail (more clearly, that the
            parameter is defined in the base class, hence we can always
            pass the scraper by)
        """
        raised = False
        try:
            scraper = pybikes.utils.PyBikesScraper()
            instance.update(scraper)
        except Exception:
            raised = True
        self.assertFalse(raised,
                         'Base class does not allow an scraper parameter')


class TestBikeShareStationInstance(unittest.TestCase):

    def setUp(self):
        self.battery = []

        stationFoo = pybikes.BikeShareStation(0)
        stationFoo.name = 'foo'
        stationFoo.latitude = 40.0149856
        stationFoo.longitude = -105.2705455
        stationFoo.bikes = 10
        stationFoo.free = 20
        stationFoo.extra = {
            'foo': 'fuzz'
        }

        stationBar = pybikes.BikeShareStation(1)
        stationBar.name = 'foo'
        stationBar.latitude = 19.4326077
        stationBar.longitude = -99.13320799999997
        stationBar.bikes = 10
        stationBar.free = 20
        stationBar.extra = {
            'bar': 'baz'
        }

        self.battery.append({
            'instance': stationFoo,
            'hash': 'e1aea428a04db6a77c4a1a091edcfcb6'
        })
        self.battery.append({
            'instance': stationBar,
            'hash': '065d7bb95e6c9079190334ee0d320c72'
        })

    def testHash(self):
        for unit in self.battery:
            self.assertEqual(
                unit['instance'].get_hash(),
                unit['hash']
            )


class TestBikeShareSystemInstance(unittest.TestCase):
    def setUp(self):

        metaFoo = {
            'name': 'Foo',
            'uname': 'foo',
            'city': 'Fooland',
            'country': 'FooEmpire',
            'latitude': 10.12312,
            'longitude': 1.12312,
            'company': 'FooCompany'
        }

        metaBar = {
            'name': 'Bar',
            'uname': 'bar',
            'city': 'Barland',
            'population': 100000
        }

        class FooSystem(pybikes.BikeShareSystem):
            pass

        class BarSystem(pybikes.BikeShareSystem):
            # Tests inheritance in meta-data:
            # - System has own meta-data
            # - Instance has also, meta-data
            # -> Hence, the result should have:
            #     1) Mandatory metadata of BikeShareSystem
            #     2) Base metadata of the system (BarSystem)
            #     3) Metadata passed on instantiation (metaBar)
            meta = {
                'company': 'BarCompany'
            }

        self.battery = []
        self.battery.append({
            'tag': 'foo',
            'meta': metaFoo,
            'instance': FooSystem('foo', metaFoo)
        })
        self.battery.append({
            'tag': 'bar',
            'meta': dict(metaBar, **BarSystem.meta),
            'instance': BarSystem('bar', metaBar)
        })

    def test_instantiation(self):
        # make sure instantiation parameters are correctly stored

        for unit in self.battery:

            self.assertEqual(unit.get('tag'), unit.get('instance').tag)

            # Check that all metainfo set on instantiation
            # appears on the instance
            for meta in unit.get('meta'):
                self.assertIn(meta, unit.get('instance').meta)
                self.assertEqual(unit.get('meta').get(meta),
                                 unit.get('instance').meta.get(meta))

            # Check that all metainfo not set on instantiation
            # appears on the instance as None
            for meta in pybikes.BikeShareSystem.meta:
                if meta not in unit.get('meta'):
                    self.assertIn(meta, unit.get('instance').meta)
                    self.assertEqual(
                        None,
                        unit.get('instance').meta.get(meta)
                    )


class TestDataFiles(unittest.TestCase):
    def setUp(self):
        self.tags = {}

    def test_instances(self):
        schemas = pybikes.get_all_data()
        for schema in schemas:
            instances = pybikes.get_instances(schema)
            for _, instance in instances:
                self._test_instance_unique(instance, schema)
                self._test_instance_fields(instance, schema)

    def _test_instance_unique(self, instance, schema):
        if instance['tag'] in self.tags:
            msg = (
                'Tag {} in {} from {} is not unique. '.format(
                    instance['tag'],
                    instance,
                    schema
                ),
                '\n Already being used by ',
                '{} in {}'.format(
                    self.tags[instance['tag']]['instance'],
                    self.tags[instance['tag']]['schema']
                )
            )
            self.fail(msg)
        self.tags[instance['tag']] = {
            'instance': instance,
            'schema': schema
        }

    def _test_instance_fields(self, instance, schema):
        self.longMessage = True
        msg = '{} contains errors. File: {}'.format(instance, schema)
        meta = instance['meta']
        # Test bare minimum definitions of networks
        self.assertIn('latitude', meta, msg=msg)
        self.assertIn('longitude', meta, msg=msg)
        self.assertIsInstance(meta['latitude'], float, msg=msg)
        self.assertIsInstance(meta['longitude'], float, msg=msg)
        self.assertIn('city', meta, msg=msg)
        self.assertIn('country', meta, msg=msg)


def create_test_schema_method(schema):
    def test_schema(self):
        self._test_systems(schema)
    return test_schema


def create_test_system_method(schema, tag):
    def test_system(self):
        key = getattr(keys, schema, None)
        self._test_system(tag, key)
    return test_system

schemas = map(lambda name: re.sub(r'\.json$', '', name), pybikes.get_all_data())
for schema in schemas:
    test_schema = create_test_schema_method(schema)
    test_schema.__name__ = 'test_%s' % schema
    setattr(TestSystems, test_schema.__name__, test_schema)
    for clsname, instance in pybikes.get_instances(schema):
        test_system = create_test_system_method(schema, instance['tag'])
        test_system.__name__ = 'test_%s' % str(instance['tag'])
        setattr(TestSystems, test_system.__name__, test_system)

if __name__ == '__main__':
    unittest.main()
