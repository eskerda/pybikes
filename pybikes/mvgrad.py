# -*- coding: utf-8 -*-
import json

from lxml import etree

from .base import BikeShareSystem, BikeShareStation
from .nextbike import Nextbike, NextbikeStation
from . import utils, exceptions

__all__ = ['Mvgrad', 'MvgradStation']

BASE_URL = 'https://mvgrad.nextbike.net/maps/nextbike-live.xml?domains=mg&get_biketypes=1'
CITY_QUERY = '/markers/country/city/place'

class Mvgrad(Nextbike):
    unifeed = False

    meta = {
        'system': 'mvgrad',
        'company': 'Münchner Verkehrsgesellschaft mbH'
    }

    def __init__(self, tag, meta, city_uid):
        super(Nextbike, self).__init__(tag, meta)
        self.url = BASE_URL
        self.uid = city_uid

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        domain_xml = etree.fromstring(
            scraper.request(self.url).encode('utf-8'))
        places = domain_xml.xpath(CITY_QUERY)
        self.stations = filter(None, map(MvgradStation, places))


class MvgradStation(NextbikeStation):
    def __init__(self, place_tree):
        super(MvgradStation, self).__init__(place_tree)

        # bike_types is a dict of bike_type : count
        # we can use this to get better numbers of available bikes
        if ('bike_types' in place_tree.attrib
            and place_tree.attrib['bikes'].endswith('+')):
            bike_types = json.loads(place_tree.attrib['bike_types'])
            self.bikes = sum(bike_types.values())
            del self.extra['bikes_approximate']

        if 'bike_racks' in place_tree.attrib:
            self.free = int(place_tree.attrib['bike_racks']) - self.bikes
            self.extra['slots'] = place_tree.attrib['bike_racks']
