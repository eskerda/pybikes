# -*- coding: utf-8 -*-
# Distributed under the LGPL license, see LICENSE.txt

import re
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['StadtradHamburg', 'StadtradHamburgStation']

# license: https://www.govdata.de/dl-de/by-2-0
BASE_URL = 'https://geodienste.hamburg.de/HH_WFS_Stadtrad?service=WFS&request=GetFeature&VERSION=1.1.0&typename' \
           '=stadtrad_stationen&outputFormat=application/geo%2bjson&srsName=EPSG:4326'


class StadtradHamburg(BikeShareSystem):
    sync = True
    unifeed = True

    meta = {
        'system': 'stadtrad_hamburg',
        'company': ['Transparenzportal Hamburg'],
        'license': {
            'name': 'Data licence Germany – attribution – version 2.0',
            'url': 'https://www.govdata.de/dl-de/by-2-0'
        }
    }

    def __init__(self, tag, meta):
        super(StadtradHamburg, self).__init__(tag, meta)
        self.url = BASE_URL

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        api_response = json.loads(scraper.request(self.url))

        self.stations = [
            StadtradHamburgStation(feature) for feature in api_response['features']
        ]


class StadtradHamburgStation(BikeShareStation):
    def __init__(self, info):
        super(StadtradHamburgStation, self).__init__()
        self.latitude = float(info['geometry']['coordinates'][1])
        self.longitude = float(info['geometry']['coordinates'][0])
        self.name = info['properties']['name'].encode("utf-8")
        self.bikes = int(info['properties']['anzahl_raeder'])
