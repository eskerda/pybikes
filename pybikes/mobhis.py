# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the LGPL license, see LICENSE.txt

import re

from lxml import html

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class Mobhis(BikeShareSystem):
    meta = {
        'system': 'Mobhis',
        'company': ['Mobhis Automação Urbana']
    }

    def __init__(self, tag, feed_url, meta):
        super(Mobhis, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        data = scraper.request(self.feed_url)

        latlngs = re.findall(r'var marker = L\.marker\(\[(-?\d+\.\d+), (-?\d+\.\d+)\]', data)
        infos = re.findall(r'marker.bindPopup\("(.*)"\)', data)
        stations = zip(latlngs, infos)
        self.stations = list(map(lambda i: MobhisStation(*i), stations))


class MobhisStation(BikeShareStation):
    def __init__(self, coords, info):
        super(MobhisStation, self).__init__()

        lat, lng = map(float, coords)

        popup = html.fromstring(info)
        elems = popup.xpath('//text()')

        self.latitude = lat
        self.longitude = lng

        online = 'Estação offline' not in info
        self.extra = {'online': online}

        # in cascavel offline stations lack name and id
        if not online:
            self.name = None
            self.bikes, self.free = 0, 0
            return

        self.name = elems.pop(0)

        fuzzle = " ".join(elems)
        bikes = re.findall(r'(\d+) bikes', fuzzle)
        slots = re.findall(r'(\d+) vagas', fuzzle)

        # there's kids bikes info
        if len(bikes) > 1 and len(slots) > 1:
            self.extra.update({
                'kid_bikes': int(bikes[1]),
                'kid_slots': int(slots[1]),
            })

        bikes, free = int(bikes[0]), int(slots[0])

        self.bikes = bikes
        self.free = free
