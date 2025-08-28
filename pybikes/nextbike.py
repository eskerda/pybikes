# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json
from lxml import etree

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.base import Vehicle, VehicleTypes
from pybikes.utils import PyBikesScraper, filter_bounds
from pybikes.contrib import TSTCache

__all__ = ['Nextbike', 'NextbikeStation']

BASE_URL = 'https://{hostname}/maps/nextbike-live.xml?domains={domain}'  # NOQA

# Since most networks share the same hostname, there's no need to keep hitting
# the endpoint on the same urls. This caches the feed for 60s
cache = TSTCache(delta=60)


class Nextbike(BikeShareSystem):
    sync = True
    unifeed = True

    meta = {
        'system': 'Nextbike',
        'company': ['Nextbike GmbH']
    }

    def __init__(self, tag, meta, domain, city_uid=None, hostname='maps.nextbike.net',
                 bbox=None):
        super(Nextbike, self).__init__(tag, meta)
        self.url = BASE_URL.format(hostname=hostname, domain=domain)
        self.domain = domain
        self.uid = city_uid
        self.bbox = bbox

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper(cache)
        domain_xml = etree.fromstring(
            scraper.request(self.url).encode('utf-8')
        )

        if self.uid:
            places = domain_xml.xpath(
                '/markers/country/city[@uid="{uid}"]/place'.format(uid=self.uid)
            )
        else:
            places = domain_xml.xpath("""
                /markers/country//city//place
            """)

        # We want to raise an error if a uid is invalid, right?
        assert places, "Not found: uid {!r}, domain {!r}, url {}".format(
            self.uid, self.domain, self.url
        )
        if self.bbox:
            def getter(place):
                lat, lng = place.attrib['lat'], place.attrib['lng']
                return (float(lat), float(lng))
            places = filter_bounds(places, getter, self.bbox)

        stations = filter(lambda p: p.attrib.get('spot', '') == '1', places)
        roaming = filter(lambda p: p.attrib.get('bike', '') == '1', places)

        self.stations = list(map(NextbikeStation, stations))
        self.vehicles = list(map(lambda p: NextbikeVehicle(p, self), roaming))


class NextbikeStation(BikeShareStation):
    def __init__(self, place):
        super(NextbikeStation, self).__init__()
        self.name = place.attrib['name']
        self.latitude = float(place.attrib['lat'])
        self.longitude = float(place.attrib['lng'])
        self.extra = {}

        self.extra['uid'] = place.attrib['uid']
        if 'number' in place.attrib:
            self.extra['number'] = place.attrib['number']

        # Greater than 5 will appear as 5+ on that case, we set bikes
        # approximate to true, to signal that the number is not exact. Note
        # this is rather frequent case for 'bike_types' and infrequent
        # corner case for 'bikes' attribute.
        if place.get('bike_types'):
            self.bikes = 0
            bike_types = json.loads(place.attrib['bike_types'])
            for value in bike_types.values():
                try:
                    self.bikes += value
                except TypeError:
                    self.bikes += int(re.sub(r'\+$', '', value))
                    self.extra['bikes_approximate'] = True
        else:
            bikes = place.attrib['bikes']
            if bikes.endswith('+'):
                self.bikes = int(re.sub(r'\+$', '', bikes))
                self.extra['bikes_approximate'] = True
            else:
                self.bikes = int(bikes)
        if 'bike_racks' in place.attrib:
            slots = int(place.attrib['bike_racks'])
            self.extra['slots'] = slots
            if 'free_racks' in place.attrib:
                self.free = int(place.attrib['free_racks'])
            else:
                self.free = slots - self.bikes
        else:
            self.free = None

        if 'bike_numbers' in place.attrib:
            bike_uids = place.attrib['bike_numbers'].split(',')
            self.extra['bike_uids'] = list(filter(None, bike_uids))

        self.extra['virtual'] = place.attrib.get('place_type') == "17"


class NextbikeVehicle(Vehicle):
    def __init__(self, place, system):

        lat = float(place.attrib['lat'])
        lng = float(place.attrib['lng'])

        extra = {
            'uid': place.xpath('./bike/@number')[0],
            'online': place.xpath('./bike/@active')[0] == '1',
        }

        super().__init__(lat, lng, extra=extra, system=system)
