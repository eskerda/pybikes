# -*- coding: utf-8 -*-
# Copyright (C) 2015, eskerda <ustroetz@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

from lxml import etree


from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper


FEED_URL = 'https://recursos-data.buenosaires.gob.ar/ckan2/ecobici/estado-ecobici.xml'


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

        namespaces = {
            'Bicicletas': 'http://bicis.buenosaires.gob.ar/ServiceBicycle.asmx'
        }

        stations_XML = tree.xpath('//Bicicletas:Estacion', namespaces=namespaces)

        stations = []
        for station_XML in stations_XML:
            station           = BikeShareStation()
            uid               = station_XML.find('Bicicletas:EstacionId', namespaces=namespaces).text
            address           = station_XML.find('Bicicletas:Lugar', namespaces=namespaces).text + ' ' + station_XML.find('{http://bicis.buenosaires.gob.ar/ServiceBicycle.asmx}Numero').text

            station.name      = station_XML.find('Bicicletas:EstacionNombre', namespaces=namespaces).text
            station.latitude  = station_XML.find('Bicicletas:Latitud', namespaces=namespaces).text
            station.longitude = station_XML.find('Bicicletas:Longitud', namespaces=namespaces).text
            station.bikes     = int(station_XML.find('Bicicletas:AnclajesTotales', namespaces=namespaces).text)
            station.free      = int(station_XML.find('Bicicletas:BicicletaDisponibles', namespaces=namespaces).text)

            station.extra = {
                'uid': uid,
                'address': address
            }

            if station.latitude and station.longitude:
                station.latitude = float(station.latitude)
                station.longitude = float(station.longitude)
                stations.append(station)

        self.stations = stations
