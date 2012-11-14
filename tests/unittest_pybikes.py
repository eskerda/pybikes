# -*- coding: utf-8 -*-
"""
Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import unittest
import json

import pybikes

from pybikes import *

class TestSystems(unittest.TestCase):

    def test_bixi(self):
        self._test_file('data/bixi.json', BixiSystem)

    def test_bcycle(self):
        self._test_file('data/bcycle.json', BCycleSystem)

    def _test_file(self, file, cls):
        f = open(file)
        data = json.loads(f.read())
        f.close()
        for system in data.get('instances'):
            sys = cls(** system)
            print(sys)
            self._test_update(sys)

    def _test_update(self, instance):
            instance.update()
            self.assertTrue(len(instance.stations)>0)

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
            'company' : 'BarCompany',
            'population' : 100000
        }

        class FooSystem(BikeShareSystem):
            tag = 'foo'
            meta = dict(BikeShareSystem.meta, **metaFoo)

        class BarSystem(BikeShareSystem):
            tag = 'bar'
            meta = dict(BikeShareSystem.meta, **metaBar)

        self.battery = []
        self.battery.append({
                        'tag': 'foo',
                        'meta': metaFoo,
                        'instance': FooSystem()
                    })
        self.battery.append({
                        'tag': 'bar',
                        'meta': metaBar,
                        'instance': BarSystem()
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
