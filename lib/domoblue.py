from station import Station
from BeautifulSoup import BeautifulStoneSoup
import urllib, urllib2
import re

HOST = "http://clientes.domoblue.es/onroll/"
SERVICE_URL = HOST+"generaXml.php?token={token}&cliente={client_id}"

TOKEN_URL = HOST+"generaMapa.php?cliente={client_id}"
TOKEN_RE = "generaXml\.php\?token\=(.*?)\&cliente"

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


"""
This headers are persistent between calls, use them in
every call, in the state they are.
"""

headers = {
	'User-Agent': 'CityBikes',
	'Accept': '*/*'
}

opener = urllib2.build_opener()


def request(url):
	req = urllib2.Request(url, headers = headers)
	response = opener.open(req)
	head = response.info()
	if 'set-cookie' in head:
		headers['Cookie'] = head['set-cookie']
	return response.read()

def get_xml(client_id):
	token = get_token(client_id)
	url = SERVICE_URL.format(token = token, client_id = client_id)
	return request(url)

def get_all():
	stations = []
	for service in SERVICES:
		for station in get_all_service(SERVICES[service]):
			stations.append(station)
	return stations

def get_token(client_id):
	url = TOKEN_URL.format(client_id = client_id)
	html_data = request(url)
	res = re.findall(TOKEN_RE, html_data)
	return res[0]

def get_services():
	xml_data = get_xml('todos')
	dom = BeautifulStoneSoup(xml_data)
	markers = dom.findAll('marker')
	services = {}
	for marker in markers:
		tmp = {
			'id': marker['codigocliente'],
			'name': marker['nombre']
		}
		tmp['service'] = slugfy(tmp['name'], '_')
		services[tmp['service']] = tmp;
	return services

def get_all_service(service):
	ID = service.get('id')
	NAME = service.get('service')
	xml_data = get_xml(ID)
	dom = BeautifulStoneSoup(xml_data)
	markers = dom.findAll('marker')
	stations = []
	for index, marker in enumerate(markers):
		station = DomoBlueStation(index,str(NAME))
		station.from_xml(marker)
		stations.append(station)
	return stations 


def slugfy(text, separator):
  ret = ""
  for c in text.lower():
    try:
      ret += htmlentitydefs.codepoint2name[ord(c)]
    except:
      ret += c
 
  ret = re.sub("([a-zA-Z])(uml|acute|grave|circ|tilde|cedil)", r"\1", ret)
  ret = re.sub("\W", " ", ret)
  ret = re.sub(" +", separator, ret)
 
  return ret.strip()

class DomoBlueStation(Station):
	def __init__(self, idx, prefix):
		Station.__init__(self,idx)
		self.prefix = prefix

	def update(self):
		return self

	def from_xml(self, xml_data):
		self.name = xml_data['nombre']
		self.lat = int(float(xml_data['lat'])*1E6)
		self.lng = int(float(xml_data['lng'])*1E6)
		self.bikes = int(xml_data['bicicletas'])
		self.free = int(xml_data['candadoslibres'])
		self.status = int(xml_data['estado'])
		return self 
