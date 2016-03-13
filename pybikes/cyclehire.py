# -*- coding: utf-8 -*-
# Copyright (C) 2016, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import demjson
from lxml import html

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes import utils


class CycleHire(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Cycle Hire',
        'company': [
            'ITS',
        ]
    }

    def __init__(self, tag, meta, feed_url):
        super(CycleHire, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        """ Looks like:
        var sites = [['<p><strong>001-Slough Train Station</strong></p>',
            51.511350,-0.591562, ,
            '<p><strong>001-Slough Train Station</strong></p>
            <p>Number of bikes available: 17</p>
            <p>Number of free docking points: 15</p>'], ...];
        """
        DATA_RGX = r'var sites = (\[.+?\]);'

        page = scraper.request(self.feed_url)
        data = re.search(DATA_RGX, page).group(1)
        _stations = demjson.decode(data)
        for _station in _stations:
            latitude = float(_station[1])
            longitude = float(_station[2])
            tree = html.fromstring(_station[4])
            name, bikes, free = tree.xpath('//p//text()')
            bikes = int(re.search(r'\d+', bikes).group())
            free = int(re.search(r'\d+', free).group())
            # Matches (<number>)<symbol?><space?>name
            uuid = re.search(r'(\d+)[\W]?\s*\w+', name)
            uuid = uuid.group(1)
            extra = {
                'uuid': uuid
            }
            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            stations.append(station)
        self.stations = stations
