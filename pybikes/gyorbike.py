# -*- coding: utf-8 -*-
# Copyright (C) 2026, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json
from lxml import html

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


ENDPOINT_URL = "https://www.gyorbike.hu/en/stations"


class GyorBike(BikeShareSystem):

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        raw = scraper.request(ENDPOINT_URL)

        # station name and detailed bike data are stored in a html table
        tree = html.fromstring(raw)

        # station coordinates and number of docks are stored in a javascript variable
        data = re.search(r'gMap.markerData=(.*);gMap.listenerParams', raw).group(1)
        data = json.loads(data)

        stations = []

        for station in data:
          # find the station element in the table
          selector = '#tr-{station_num}'.format(station_num=station["station_num"])
          station_element = tree.cssselect(selector)[0]
          if station_element is not None:
            stations.append(GyorbikeStation(station, station_element))

        self.stations = stations


class GyorbikeStation(BikeShareStation):
    @staticmethod
    def _get_int_field(element, title):
        text = element.cssselect(f'[data-title="{title}"] .inner')[0].text_content()
        # return 0 if offline
        return 0 if '--' in text else int(text)

    @staticmethod
    def _get_name(element):
        text = element.cssselect('[data-title="Station name"] .inner')[0].text_content()
        # remove "offline" suffix in station name
        return text.split('Offline')[0].strip()
    
    def __init__(self, data, station_element):
        super(GyorbikeStation, self).__init__()

        self.latitude = float(data["lat"])
        self.longitude = float(data["lng"]) 
        self.name = self._get_name(station_element)

        mechanical_bikes = self._get_int_field(station_element, "Standard bike")
        ebikes = self._get_int_field(station_element, "E-bike")
        free = self._get_int_field(station_element, "Available dock")

        self.bikes = mechanical_bikes + ebikes
        self.free = free

        self.extra = {
            'uid': data["station_num"],
            'slots': data["docks"],
            'mechanical_bikes': mechanical_bikes,
            'has_ebikes': ebikes > 0,
            'ebikes': ebikes,
            'online': 'offline' not in station_element.get('class', '')
        }
