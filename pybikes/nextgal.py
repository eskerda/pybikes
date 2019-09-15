# -*- coding: utf-8 -*-

try:
    # Python 2
    from urlparse import urljoin
except ImportError:
    # Python 3
    from urllib.parse import urljoin

from lxml import etree

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper

PATH = '/swm/WSMobile.asmx'

NS = {
    'ab': 'http://aparcabicis.nextgal.es/'
}

PAYLOAD = """<?xml version='1.0' encoding='UTF-8'?>
<v:Envelope xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns:d="http://www.w3.org/2001/XMLSchema" xmlns:c="http://schemas.xmlsoap.org/soap/encoding/"
xmlns:v="http://schemas.xmlsoap.org/soap/envelope/">
  <v:Header/>
  <v:Body>
    <GetEstaciones xmlns="http://aparcabicis.nextgal.es/" id="o0" c:root="1"/>
  </v:Body>
</v:Envelope>"""


class Nextgal(BikeShareSystem):
    meta = {
        'system': 'Tuimil',
        'company': ['Tuimil S.A.'],
    }

    def __init__(self, tag, meta, url):
        super(Nextgal, self).__init__(tag, meta)
        self.url = url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        scraper.setUserAgent('kSOAP/2.0')
        scraper.headers.update({
            'SOAPAction': 'http://aparcabicis.nextgal.es/GetEstaciones',
            'Content-Type': 'text/xml',
        })
        data = scraper.request(urljoin(self.url, PATH), method='POST',
                               data=PAYLOAD)
        tree = etree.XML(data.encode('utf-8'))
        stations_xml = tree.xpath('//ab:EstacionAdditionalInformationDto',
                                  namespaces=NS)
        self.stations = map(NextgalStation, stations_xml)


class NextgalStation(BikeShareStation):
    def __init__(self, data):
        self.name = data.findtext('ab:Nombre', namespaces=NS)
        self.latitude = float(data.findtext('ab:Latitud', namespaces=NS))
        self.longitude = float(data.findtext('ab:Longitud', namespaces=NS))
        self.bikes = int(data.findtext('ab:BicisDisponibles', namespaces=NS))
        self.free = int(data.findtext('ab:PuestosLibres', namespaces=NS))

        status = data.findtext('ab:IsOnline', namespaces=NS)
        self.extra = {
            # For this system, it's accurate to say that the total number of
            # slots is the sum of bikes and free spots (no status / error)
            'slots': self.bikes + self.free,
            'status': 'online' if status == 'true' else 'offline',
            'uid': data.findtext('ab:IdEstacion', namespaces=NS),
        }
