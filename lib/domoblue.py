from station import Station
from BeautifulSoup import BeautifulStoneSoup
import urllib, urllib2

URL = "http://clientes.domoblue.es/onroll/generaXml.php?cliente=%d"

SERVICES = {
	'albacete':{'id':2,'name':'albacete'},
	'alhamademurcia':{'id':37,'name':'alhamademurcia'},
	'almunecar':{'id':70,'name':'almunecar'},
	'antequera':{'id':29,'name':'antequera'},
	'arandadeduero':{'id':68,'name':'arandadeduero'},
	'arua':{'id':64,'name':'arua'},
	'badajoz':{'id':49,'name':'badajoz'},
	'baeza':{'id':25,'name':'baeza'},
	'biciambiental':{'id':69,'name':'biciambiental'},
	'bicielx':{'id':57,'name':'bicielx'},
	'blanca':{'id':59,'name':'blanca'},
	'cieza':{'id':61,'name':'cieza'},
	'ciudadreal':{'id':3,'name':'ciudadreal'},
	'elcampello':{'id':41,'name':'elcampello'},
	'guadalajara':{'id':43,'name':'guadalajara'},
	'jaen':{'id':26,'name':'jaen'},
	'lalin':{'id':62,'name':'lalin'},
	'montilla':{'id':28,'name':'montilla'},
	'mula':{'id':56,'name':'mula'},
	'novelda':{'id':50,'name':'novelda'},
	'obarco':{'id':67,'name':'obarco'},
	'paiporta':{'id':47,'name':'paiporta'},
	'palencia':{'id':7,'name':'palencia'},
	'priegodecordoba':{'id':27,'name':'priegodecordoba'},
	'puertollano':{'id':1,'name':'puertollano'},
	'puertolumbreras':{'id':60,'name':'puertolumbreras'},
	'redondela':{'id':44,'name':'redondela'},
	'salamanca':{'id':65,'name':'salamanca'},
	'sanjavier':{'id':38,'name':'sanjavier'},
	'sanpedrodelpinatar':{'id':20,'name':'sanpedrodelpinatar'},
	'santjoan':{'id':45,'name':'santjoan'},
	'segovia':{'id':5,'name':'segovia'},
	'soria':{'id':46,'name':'soria'},
	'talavera':{'id':4,'name':'talavera'},
	'ubeda':{'id':24,'name':'ubeda'},
	'ugr':{'id':30,'name':'ugr'},
	'viaverde':{'id':63,'name':'viaverde'},
	'vigo':{'id':71,'name':'vigo'},
	'vilarreal':{'id':19,'name':'vilarreal'},
	'villanuevadonbenito':{'id':53,'name':'villanuevadonbenito'},
	'villaquilambre':{'id':6,'name':'villaquilambre'},
	'vinaros':{'id':51,'name':'vinaros'}
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
