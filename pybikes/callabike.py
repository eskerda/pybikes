# -*- coding: utf-8 -*-
# Copyright (C) 2015, David Kreitschmann <david@kreitschmann.de>
# Distributed under the AGPL license, see LICENSE.txt
import re
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['Callabike', 'CallabikeStation']

BASE_URL = 'https://www.callabike-interaktiv.de/kundenbuchung/hal2ajax_process.php?callee=getMarker&mapstadt_id={city_id}&requester=bikesuche&ajxmod=hal2map&bereich=2&buchungsanfrage=N&webfirma_id=500&searchmode=default'


class Callabike(BikeShareSystem):
    sync = True
    unifeed = True

    meta = {
        'system': 'Call-A-Bike',
        'company': ['DB Rent GmbH']
    }

    def __init__(self, tag, meta, city_id):
        super(Callabike, self).__init__(tag, meta)
        self.url = BASE_URL.format(city_id=city_id)

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        markers = json.loads(scraper.request(self.url))
        self.stations = [
            CallabikeStation(a) for a in markers['marker']
            if a['hal2option']['standort_id']
        ]


class CallabikeStation(BikeShareStation):
    def __init__(self, info):
        super(CallabikeStation, self).__init__()
        self.latitude = float(info['lat'])
        self.longitude = float(info['lng'])

        hal2 = info['hal2option']
        tooltip = hal2['tooltip']
        tooltip = tooltip.replace("&nbsp;", " ")
        tooltip = re.sub(r"^'|'$", "", tooltip)
        tooltip = tooltip.strip()
        tooltip = tooltip.encode("utf-8")
        bikes = hal2['bikelist']
        bikes = [a for a in bikes if a['canBeRented']]

        self.name = tooltip
        self.bikes = len(bikes)
