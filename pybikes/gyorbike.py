# -*- coding: utf-8 -*-
# Copyright (C) 2026, Martín González Gómez <m@martingonzalez.net>
# Copyright (C) 2026, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json
from warnings import warn

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

        rows = tree.xpath('//table[@id="cmeStationInfo"]/tr')
        row_id_map = {
            re.sub(r'tr-', '', row.xpath('./@id')[0]): row
            for row in rows
        }

        for station in data:
            uid = str(station["station_num"])
            if uid not in row_id_map:
                warn("Station %s not found in html table", station)
                continue
            stations.append(GyorbikeStation(station, row_id_map[uid]))

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
            'normal_bikes': mechanical_bikes,
            'ebikes': ebikes,
            'online': 'offline' not in station_element.get('class', '')
        }
