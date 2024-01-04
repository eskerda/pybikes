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

        # in cascavel offline stations lack name and id
        name = elems.pop(0)
        if 'Estação offline' in name:
            name = ''
            uid = ''
        else:
            uid, _ = name.split(' - ')

        online = 'Estação offline' not in info

        self.name = name
        self.latitude = lat
        self.longitude = lng
        self.extra = {'uid': uid, 'online': online}

        if not online:
            self.bikes, self.free = 0, 0
            return

        # find ints on remaining elements
        elems = list(map(lambda s: re.search(r'\d+', s).group(), elems))

        # some systems have data for kid-sized bikes and spaces
        if len(elems) > 2:
            bikes, bikes_kids, free, free_kids = elems
            self.extra.update({
                'kid_bikes': int(bikes_kids),
                'kid_slots': int(free_kids),
            })
        else:
            bikes, free = elems

        self.bikes = int(bikes)
        self.free = int(free)
