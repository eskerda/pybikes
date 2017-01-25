# -*- coding: utf-8 -*-
# Copyright (C) 2017, Alberto Varela <alberto@berriart.com>
# Distributed under the AGPL license, see LICENSE.txt

from lxml import etree

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper

__all__ = ['BilbonBizi']

class BilbonBizi(BikeShareSystem):
    sync = True

    meta = {
        'system': 'BilbonBizi',
        'company': ['Ayuntamiento de Bilbao'],
        'license': {
            'name': 'Creative Commons Reconocimiento 3.0 España',
            'url': 'https://creativecommons.org/licenses/by/3.0/es/'
        },
        'source': 'https://www.bilbao.eus/opendata/es/catalogo/dato-puntos-recogida-bicicletas-en-prestamo'
    }

    def __init__(self, tag, meta, feed_url):
        super(BilbonBizi, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper()
        raw = scraper.request(self.feed_url, 'GET', None, None, True)
        tree = etree.fromstring(raw)
        stationList = tree.xpath('/RESPUESTA/LISTA/DETALLE')

        self.stations = map(BilbonBiziStation, stationList)


class BilbonBiziStation(BikeShareStation):
    def __init__(self, station):
        super(BilbonBiziStation, self).__init__()
        self.name = station.find('NOMBRE').text
        self.latitude = float(station.find('LATITUD').text)
        self.longitude = float(station.find('LONGITUD').text)
        self.bikes = int(station.find('BLIBRES').text)
        self.free = int(station.find('ALIBRES').text)
        self.extra = {
            'uid': int(station.find('ID').text),
            'online': station.find('ESTADO').text != "NO COMUNICA"
        }
