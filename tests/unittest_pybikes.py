# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import unittest
from pkg_resources import resource_string
import json

import sys

import pybikes
from pybikes import *
from pybikes import utils
import test_keys

class TestSystems(unittest.TestCase):

    def test_bixi(self):
        self._test_systems('bixi')

    def test_bcycle(self):
        self._test_systems('bcycle')

    def test_cyclocity(self):
        self._test_systems('cyclocity')

    def test_gewista(self):
        self._test_systems('gewista')

    def test_smartbike(self):
        self._test_systems('smartbike')

    def test_decobike(self):
        self._test_systems('decobike')

    def test_keolis(self):
        self._test_systems('keolis')

    def _test_systems(self, system):
        data = pybikes.getDataFile(system)
        if isinstance(data['class'], unicode):
            sys_class = eval(data['class'])
            if sys_class.authed:
                key = eval('test_keys.%s' % system)
            else:
                key = None
            for instance in data['instances']:
                self._test_system(system, instance['tag'], key)
        elif isinstance(data['class'], dict):
            for cls in data['class']:
                sys_class = eval(cls)
                if sys_class.authed:
                    key = eval('test_keys.%s' % system)
                else:
                    key = None
                for instance in data['class'][cls]['instances']:
                    self._test_system(system, instance['tag'], key)
        else:
            raise Exception('Malformed data file')

    def _test_system(self, system, tag, key = None):
        """ Tests okayness of a system:
            - Test if system can be updated
            - Tests okayness of 5 stations on the system
        """
        p_sys = pybikes.getBikeShareSystem(system, tag, key)
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

        self.assertIsNotNone(station.bikes)
        self.assertIsNotNone(station.free)
        self.assertIsNotNone(station.latitude)
        self.assertIsNotNone(station.longitude)
        self.assertIsNotNone(station.name)

    def _test_update(self, instance):
        """ Tests if this system can be updated
            we assume that having more than 0 stations
            means being updateable. Also, test if its update function
            allows a PyBikesScraper parameter
        """
        instance.update()
        print "%s has %d stations" % (
            instance.meta['name'], len(instance.stations)
        )
        self.assertTrue(len(instance.stations)>0)
        self._test_allows_parameter(instance)

    def _test_allows_parameter(self, instance):
        """ Tests if this instance, be it a system or a station, allows a
            PyBikesScraper parameter for its update method
        """
        scraper = utils.PyBikesScraper()
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
            scraper = utils.PyBikesScraper()
            instance.update(scraper)
        except Exception:
            raised = True
        self.assertFalse(raised, 'Base class does not allow an scraper parameter')


class TestBikeShareStationInstance(unittest.TestCase):

    def setUp(self):
        self.battery = []

        stationFoo = BikeShareStation(0)
        stationFoo.name = 'foo'
        stationFoo.latitude = 40.0149856
        stationFoo.longitude = -105.2705455
        stationFoo.bikes = 10
        stationFoo.free = 20
        stationFoo.extra = {
            'foo': 'fuzz'
        }

        stationBar = BikeShareStation(1)
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
            'name' : 'Foo',
            'uname' : 'foo',
            'city' : 'Fooland',
            'country' : 'FooEmpire',
            'latitude' : 10.12312,
            'longitude' : 1.12312,
            'company' : 'FooCompany'
        }

        metaBar = {
            'name' : 'Bar',
            'uname' : 'bar',
            'city' : 'Barland',
            'population' : 100000
        }

        class FooSystem(BikeShareSystem):
            pass

        class BarSystem(BikeShareSystem):
            # Tests inheritance in meta-data:
            # - System has own meta-data
            # - Instance has also, meta-data
            # -> Hence, the result should have:
            #     1) Mandatory metadata of BikeShareSystem
            #     2) Base metadata of the system (BarSystem)
            #     3) Metadata passed on instantiation (metaBar)
            meta = {
                'company' : 'BarCompany'
            }

        self.battery = []
        self.battery.append({
                        'tag': 'foo',
                        'meta': metaFoo,
                        'instance': FooSystem('foo', metaFoo)
                    })
        self.battery.append({
                        'tag': 'bar',
                        'meta': dict(metaBar,**BarSystem.meta),
                        'instance': BarSystem('bar',metaBar)
                    })

    def test_instantiation(self):
        # make sure instantiation parameters are correctly stored

        for unit in self.battery:
            
            self.assertEqual(unit.get('tag'), unit.get('instance').tag)

            # Check that all metainfo set on instantiation
            # appears on the instance
            for meta in unit.get('meta'):
                self.assertIn(meta,unit.get('instance').meta)
                self.assertEqual(
                        unit.get('meta').get(meta), 
                        unit.get('instance').meta.get(meta)
                    )

            # Check that all metainfo not set on instantiation
            # appears on the instance as None
            for meta in BikeShareSystem.meta:
                if meta not in unit.get('meta'):
                    self.assertIn(meta, unit.get('instance').meta)
                    self.assertEqual(
                        None, 
                        unit.get('instance').meta.get(meta)
                    )

if __name__ == '__main__':
    unittest.main()
