# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import re

from lxml import etree

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Domoblue']

MAIN = 'http://clientes.domoblue.es/onroll/'
TOKEN_URL = 'generaMapa.php?cliente={service}&ancho=500&alto=700'
XML_URL = 'generaXml.php?token={token}&cliente={service}'
TOKEN_RE = 'generaXml\.php\?token\=(.*?)\&cliente'
USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, '\
             'like Gecko) Chrome/18.0.1025.168 Safari/535.19'
STATUS_CODES = {
    14: 'Online',
    16: 'No Power',
    17: 'No Service'
}


def get_token(client_id, scraper):
    if 'Referer' in scraper.headers:
        del(scraper.headers['Referer'])
    url = MAIN + TOKEN_URL.format(service=client_id)
    data = scraper.request(url)
    token = re.findall(TOKEN_RE, data)
    scraper.headers['Referer'] = url
    return token[0]


def get_xml(client_id, scraper):
    token = get_token(client_id, scraper)
    url = MAIN + XML_URL.format(token=token, service=client_id)
    return scraper.request(url)


class Domoblue(BikeShareSystem):
    sync = True
    meta = {
        'system': 'Onroll',
        'company': ['Domoblue']
    }

    def __init__(self, tag, meta, system_id):
        super(Domoblue, self).__init__(tag, meta)
        self.system_id = system_id


    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.setUserAgent(USER_AGENT)

        xml_data = get_xml(self.system_id, scraper)
        xml_data = xml_data
        xml_dom = etree.fromstring(xml_data)
        stations = []
        for index, marker in enumerate(xml_dom.xpath('//marker')):
            station = BikeShareStation(index)
            station.name        = marker.get('nombre')
            station.bikes       = int(marker.get('bicicletas'))
            station.free        = int(marker.get('candadosLibres'))
            station.latitude    = float(marker.get('lat'))
            station.longitude   = float(marker.get('lng'))
            status_code         = int(marker.get('estado'))
            station.extra = {
                'status': {
                    'code':    status_code,
                    'online':  (lambda c: c == 14)(status_code),
                    'message': (lambda c: \
                                    STATUS_CODES[c] if c in STATUS_CODES \
                                                    else 'Planned'\
                               )(status_code)
                }
            }
            # Uppercase is UGLY, do not shout at me domoblue!
            station.name = utils.sp_capwords(station.name)

            stations.append(station)
        self.stations = stations
