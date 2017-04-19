import unittest
import suds
 
class TestBiciCorunha(unittest.TestCase):
 
    def setUp(self):
        self.client=suds.client.Client('http://www.bicicoruna.es/wservices/wstatus.asmx?WSDL')
 
    def test_GetEstaciones_should_return_a_collection_of_station(self):
        data = self.client.service.GetEstaciones()
        stations = data[0]

        self.assertTrue( len(stations) > 0)

    def test_GetEstaciones_should_return_valid_stations(self):
        data = self.client.service.GetEstaciones()
        station = data[0][0]

        self.assertIsInstance(station.Nombre, suds.sax.text.Text)
        self.assertIsInstance(station.Latitud, float)
        self.assertIsInstance(station.Longitud, float)
        self.assertIsInstance(station.TotalPuestosOcupados, int)
        self.assertIsInstance(station.TotalPuestosActivos, int)
 
if __name__ == '__main__':
    unittest.main()