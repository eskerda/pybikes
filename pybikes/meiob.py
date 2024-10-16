# -*- coding: utf-8 -*-
# Copyright (C) 2024, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

from lxml import html

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class Meiob(BikeShareSystem):

    def __init__(self, tag, meta, endpoint):
        super(Meiob, self).__init__(tag, meta)

        self.endpoint = endpoint

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        stations = []
        raw = scraper.request(self.endpoint)
        tree = html.fromstring(raw)
        station_elements = tree.cssselect('.bikes > .bike')

        for station_element in station_elements:
            station = MeiobStation(station_element)
            stations.append(station)

        self.stations = stations

class MeiobStation(BikeShareStation):
    def __init__(self, station):
        super(MeiobStation, self).__init__()

        self.latitude = float(station.cssselect('.stationlat')[0].text_content())
        self.longitude = float(station.cssselect('.stationlon')[0].text_content())

        # usually name is on the second element but not always
        parsed_name = station.cssselect('.stationlon + .border-right-blue > h2')[0].text_content().split(' - ')
        if len(parsed_name) == 2:
          self.name = parsed_name[1]
        else:
          self.name = parsed_name[0]

        bikes, free = station.cssselect('.bike__available')
        self.bikes = int(bikes.text_content())
        self.free = int(free.text_content())

        address, city = station.cssselect('.bike__distance__title')
        self.extra = {
          'address': address.text_content(),
          'city': city.text_content()
        }
