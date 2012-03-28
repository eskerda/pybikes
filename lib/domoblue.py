from station import Station
from BeautifulSoup import BeautifulStoneSoup
import urllib, urllib2

URL = "http://clientes.domoblue.es/onroll/generaXml.php?cliente=%d"

SERVICES = {
	'puertobike':{'id':1,'name':'puertobike'},
	'bicilex':{'id':57,'name':'bicilex'}
}

def get_all(prefix = ""):
	stations = []
	for service in SERVICES:
		for station in get_all_service(service,prefix):
			stations.append(station)
	return stations
def get_all_service(service,prefix = ""):
	ID = SERVICES[service].get('id')
	NAME = SERVICES[service].get('name')
	request = urllib.urlopen(prefix+URL%ID)
	xml_data = request.read()
	request.close()
	dom = BeautifulStoneSoup(xml_data)
	markers = dom.findAll('marker')
	stations = []
	for index, marker in enumerate(markers):
		station = DomoBlueStation(index,NAME)
		station.from_xml(marker)
		stations.append(station)
	return stations 

class DomoBlueStation(Station):
	def __init__(self, idx, pfx):
		Station.__init__(self,idx)
		self.prefix = pfx

	def update(self, prefix=""):
		return self

	def from_xml(self, xml_data):
		self.name = xml_data['nombre']
		self.lat = int(float(xml_data['lat'])*1E6)
		self.lng = int(float(xml_data['lng'])*1E6)
		self.bikes = int(xml_data['bicicletas'])
		self.free = int(xml_data['candadoslibres'])
		self.status = int(xml_data['estado'])
		return self 
