import unittest
from pybikes import BikeShareSystem

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

		# Instance foo has all the metadata complete, and includes
		# no extra metadata
		instanceFoo = BikeShareSystem('foo',metaFoo)
		
		# Instance bar has does not have all the basic metadata
		# set, but has extra metadata
		instanceBar = BikeShareSystem('bar',metaBar)

		self.battery = []
		self.battery.append({
						'tag': 'foo',
						'meta': metaFoo,
						'instance': instanceFoo
					})
		self.battery.append({
						'tag': 'bar',
						'meta': metaBar,
						'instance': instanceBar
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
