# -*- coding: utf-8 -*-

from lxml import etree

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper
from pybikes.exceptions import InvalidStation

FEED_URL = 'https://recursos-data.buenosaires.gob.ar/ckan2/ecobici/estado-ecobici.xml'  # NOQA

NS = {
    'b': 'http://bicis.buenosaires.gob.ar/ServiceBicycle.asmx'
}


class EcobiciBA(BikeShareSystem):
    sync = True

    meta = {
        'system': 'BA Ecobici',
        'company': 'Buenos Aires Ciudad',
        'license': {
            'name': 'Terms of Service',
            'url': 'http://data.buenosaires.gob.ar/tyc'
        }
    }

    def __init__(self, tag, meta):
        super(EcobiciBA, self).__init__(tag, meta)
        self.feed_url = FEED_URL

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper()
        data = scraper.request(self.feed_url)
        tree = etree.XML(data.encode('utf-8'))

        stations_xml = tree.xpath('//b:Estacion', namespaces=NS)
        stations = []
        for station_xml in stations_xml:
            try:
                station = EcobiciBAStation(station_xml)
            except InvalidStation:
                continue
            stations.append(station)
        self.stations = stations


class EcobiciBAStation(BikeShareStation):
    def __init__(self, data):
        super(EcobiciBAStation, self).__init__()
        try:
            self.name = data.findtext('b:EstacionNombre', namespaces=NS)
            self.latitude = float(data.findtext('b:Latitud', namespaces=NS))
            self.longitude = float(data.findtext('b:Longitud', namespaces=NS))
            self.bikes = int(data.findtext('b:BicicletaDisponibles',
                                           namespaces=NS))
            self.free = int(data.findtext('b:AnclajesDisponibles',
                                          namespaces=NS))
        except Exception:
            raise InvalidStation()

        if 'pruebas' in self.name.lower():
            raise InvalidStation()

        address = data.findtext('b:Lugar', namespaces=NS)
        number = data.findtext('b:Numero', namespaces=NS)
        if number != '0':
            address = u'{} {}'.format(address, number)
        status = data.findtext('b:EstacionDisponible', namespaces=NS)
        self.extra = {
            'uid': data.findtext('b:EstacionId', namespaces=NS),
            'address': address,
            'status': 'open' if status == 'SI' else 'closed',
            'slots': int(data.findtext('b:AnclajesTotales', namespaces=NS))
        }
