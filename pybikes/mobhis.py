# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the LGPL license, see LICENSE.txt

import re

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

        html = scraper.request(self.feed_url)

        # coords are on the first line, info on the second
        pattern = r'var marker = L\.marker\((.*?)\)\.addTo\(map\);\n(.*?)(?=\n\n|\n\Z)'
        all = re.findall(pattern, html, re.DOTALL)

        # filter out offline stations
        stations = filter(lambda item: item[1].find('Estação offline ou não instalada') == -1, all)

        self.stations = list(map(lambda d: MobhisStation(* d), stations))


class MobhisStation(BikeShareStation):
    def __init__(self, coords, info):
        super(MobhisStation, self).__init__()

        lat, lon = re.search(r'\[([^\]]+)\]', coords).group(1).split(', ')
        id, name = re.search(r'bindPopup\("<center><b>([^<]+)</b>', info).group(1).split(' - ')

        info = re.search(r'</b>(.*?)</center>', info).group(1).split('<br>')
        info = list(filter(lambda item: item != '', info))
        info = list(map(lambda s: re.findall(r'\d+', s)[0], info))

        bikes_kids = None
        free_kids = None

        # some systems have data for kid-sized bikes and spaces
        if len(info) > 2:
            bikes, bikes_kids, free, free_kids = info
        else:
           bikes, free = info

        self.name = name
        self.latitude = float(lat)
        self.longitude = float(lon)
        self.bikes = int(bikes)
        self.free = int(free)
        self.extra = {
            'uid': id
        }

        if bikes_kids:
            self.extra['bikes_kids'] = int(bikes_kids)
        if free_kids:
            self.extra['free_kids'] = int(free_kids)
