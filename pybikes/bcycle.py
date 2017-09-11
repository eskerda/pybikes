# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re

from lxml import html
from .base import BikeShareSystem, BikeShareStation
from .exceptions import InvalidStation
from . import utils

__all__ = ['BCycleSystem', 'BCycleStation']

LAT_LNG_RGX = "var\ point\ =\ new\ google.maps.LatLng\(([+-]?\\d*\\.\\d+)(?![-+0-9\\.])\,\ ([+-]?\\d*\\.\\d+)(?![-+0-9\\.])\)"
DATA_RGX = "var\ marker\ =\ new\ createMarker\(point\,(.*?)\,\ icon\,\ back"
USERAGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/31.0.1650.63 Chrome/31.0.1650.63 Safari/537.36"

class BCyclePurgatoryException(Exception):
    """
    Purgatory stations are only used for bikes that are lost, pending recovery.
    It has no bike slots so it shouldn't be considered a valid station.
    """
    pass

class BCycleSystem(BikeShareSystem):

    feed_url = "http://{system}.bcycle.com"
    sync = True

    meta = {
        'system': 'B-cycle',
        'company': [ 'Trek Bicycle Corporation'
                     ,'Humana'
                     ,'Crispin Porter + Bogusky' ]
    }

    def __init__(self, tag, meta, system = None, feed_url = None):
        super( BCycleSystem, self).__init__(tag, meta)

        if feed_url is not None:
            self.feed_url = feed_url
        else:
            self.feed_url = BCycleSystem.feed_url.format(system =  system)

    def update(self, scraper = None):

        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.setUserAgent(USERAGENT)

        html_data = scraper.request(self.feed_url)

        geopoints = re.findall(LAT_LNG_RGX, html_data)
        puzzle = re.findall(DATA_RGX, html_data)

        for latlng, fuzzle in zip(geopoints, puzzle):
            try:
                self.stations.append(BCycleStation(latlng, fuzzle))
            except (InvalidStation, BCyclePurgatoryException):
                pass

class BCycleStation(BikeShareStation):
    def __init__(self, latlng, fuzzle):
        """ Take a good look at this fuzzle:
            var point = new google.maps.LatLng(41.86727, -87.61527);
            var marker = new createMarker(
                point,                       .--- Fuzzle
                "<div class='location'>      '
                    <strong>Museum Campus</strong><br />
                    1200 S Lakeshore Drive<br />
                    Chicago, IL 60605
                </div>
                <div class='avail'>
                    Bikes available: <strong>0</strong><br />
                    Docks available: <strong>21</strong>
                </div>
                <br/>
                ", icon, back);
            Now, do something about it
        """
        super(BCycleStation, self).__init__()
        dom = html.fromstring(fuzzle)

        try:
            name, = dom.xpath("//div[@class='location']/strong/text()")

            if name.lower() == 'purgatory':
                raise BCyclePurgatoryException

            address = dom.xpath("//div[@class='location']/text()")
            bikes, free = dom.xpath("//div[@class='avail']/strong/text()")

        except ValueError:
            name, = dom.xpath("//div[@class='markerPublicText']/h5/text()")

            if name.lower() == 'purgatory':
                raise BCyclePurgatoryException

            address = dom.xpath("//div[@class='markerAddress']/text()")
            availability = dom.xpath("//div[@class='markerAvail']//h3/text()")
            # Special events marker has no availability information, discard it.
            if not availability:
                raise InvalidStation
            bikes = availability[0]
            free = availability[1]

        self.name = name
        self.latitude = float(latlng[0])
        self.longitude = float(latlng[1])
        self.bikes = int(bikes)
        self.free = int(free)
        self.extra = {
            'address': ", ".join(address)
        }