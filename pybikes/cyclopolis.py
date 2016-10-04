# -*- coding: utf-8 -*-
# Copyright (C) 2015, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['Cyclopolis', 'CyclopolisStation']

LAT_LNG_RGX = r'latLng:\[(\d+.\d+).*?(\d+.\d+)\]'
DATA_RGX = r'data\:.*?<span.*?>(.*?)</span>'

"""
In some systems, e.g., maroussi, nafplio, stations come as:
{
  latLng: [37.5639397319061000, 22.8093402871746000],
  data: "<div style='line-height:1.35;overflow:hidden;white-space:nowrap;'>
             <span style='color:#333333'>
                <b>ETHNOSINELFSIS SQUARE<br/>available bikes: n/a</b>
                <br/>capacity: 32<br/>free:n/a<br/>offline
             </span>
         </div>",
  options: {
    icon: "http://nafplio.cyclopolis.gr//images/markers/red-03.png"
  }
}
In other systems, e.g., aigialeia, it is shorter, there is no 'div' tag:
    data:"<span style='color:#333333'>
            <b>ΨΗΛΑ ΑΛΩΝΙΑ</b>
            <br/>χωρητικοτητα: 16<br/>ελεύθερες θεσεις:n/a<br/>offline
        </span>"
"""

class Cyclopolis(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Cyclopolis',
        'company': ['Cyclopolis Systems']
    }

    def __init__(self, tag, feed_url, meta):
        super(Cyclopolis, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        html = scraper.request(self.feed_url)
        data = zip(
            re.findall(LAT_LNG_RGX, html, re.DOTALL),
            re.findall(DATA_RGX, html, re.DOTALL)
        )
        for lat_lng, info in data:
            latitude = float(lat_lng[0])
            longitude = float(lat_lng[1])
            fields = info.replace('<b>','').replace('</b>','').split('<br/>')
            extra = {}
            if len(fields) == 4: # there is not slots information available
                name, raw_bikes, raw_free, status = fields
            else:
                name, raw_bikes, raw_slots, raw_free, status = fields
                slots = int(raw_slots.split(':')[-1])
                extra['slots'] = slots
            # In some circumstances, e.g., station is offline,
            # the number of 'bikes' and/or 'free' is 'n/a'
            try:
                bikes = int(raw_bikes.split(':')[-1])
            except ValueError:
                bikes = 0
            try:
                free = int(raw_free.split(':')[-1])
            except ValueError:
                free = 0
            if status == 'offline':
                extra['closed'] = True
            station = CyclopolisStation(name, latitude, longitude,
                                        bikes, free, extra)
            stations.append(station)
        self.stations = stations

class CyclopolisStation(BikeShareStation):
    def __init__(self, name, latitude, longitude, bikes, free, extra):
        super(CyclopolisStation, self).__init__()

        self.name      = name
        self.latitude  = latitude
        self.longitude = longitude
        self.bikes     = bikes
        self.free      = free
        self.extra     = extra
