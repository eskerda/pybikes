# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import re
from lxml import etree

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.utils import filter_bounds

BASE_URL = 'https://www.mibisivalencia.es/{tag}/mapa.php'

def get_int(str):
    match = re.search(r'\d+', str)
    if match:
        return int(match.group())
    return 0

class MiBisiValencia(BikeShareSystem):
    sync = True

    meta = {
        'system': 'MiBisiValencia',
        'company': ['Movilidad Urbana Sostenible SLU']
    }

    def __init__(self, tag, meta):
        super(MiBisiValencia, self).__init__(tag, meta)
        self.url = BASE_URL.format(tag=tag)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        raw = scraper.request(self.url)
        raw = etree.HTML(raw)

        stations = []

        script = raw.xpath('//script[contains(text(), "var misPuntos")]')
        javascript_code = script[0].text_content()

        for div in raw.xpath('//div[@class="hiright"]'):
            for entry in div.xpath('.//img'):
                stations.append(MiBisiValenciaStation(entry))
        self.stations = stations

class MiBisiValenciaStation(BikeShareStation):
    def __init__(self, html):
        super(MiBisiValenciaStation, self).__init__()

        for div in html.xpath('//div[@class="hiright"]'):
            for entry in div.xpath('.//img'):
                self.name = entry.xpath('string(following-sibling::text()[1])').strip()
                self.bikes = get_int(entry.xpath('./following-sibling::text()[1]')[0].strip())
                self.free = get_int(entry.xpath('./following-sibling::text()[2]')[0].strip())
                # TK
                self.longitude = 0.1
                self.latitude = 0.1
