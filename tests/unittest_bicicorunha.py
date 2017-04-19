import sys,os
sys.path.insert(0,os.path.abspath(__file__+"/../.."))

import unittest
from pybikes.bicicorunha import BicicorunhaClient
from pybikes.base import BikeShareStation
 
class TestBiciCorunha(unittest.TestCase):
 
    def setUp(self):
        self.client = BicicorunhaClient(ClientStub)

    def test_getStations_should_return_valid_stations(self):
        stations = self.client.getStations()

        self.assertTrue( len(stations) > 0)
        self.assertIsInstance(stations[0], BikeShareStation)
        self.assertEqual(stations[0].name, 'Nombre')
        self.assertEqual(stations[0].latitude, 1.1)
        self.assertEqual(stations[0].longitude, 2.2)
        self.assertEqual(stations[0].bikes, 10)
        self.assertEqual(stations[0].free, 2)
    
class EstacionStub():
    Nombre = "Nombre"
    Latitud = 1.1
    Longitud = 2.2
    TotalPuestosOcupados = 10
    TotalPuestosActivos = 12

class ServiceStub():
    def GetEstaciones(self):
        return [[EstacionStub()]]

class ClientStub():
    service = ServiceStub()
 
if __name__ == '__main__':
    unittest.main()