# -*- coding: utf-8 -*-
import re
import json
import zlib
from pkg_resources import resource_string
from itertools import imap

from lxml import etree
from shapely.geometry import Polygon, Point

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper
from pybikes.contrib import TSTCache


_kml_ns = {
    'kml': 'http://earth.google.com/kml/2.2'
}

cache = TSTCache(delta=60)


class YouBike(BikeShareSystem):
    meta = {
        'system': 'YouBike',
        'company': [
            'Taipei City Government',
            'Giant Manufacturing Co. Ltd.',
        ]
    }

    main_url = 'http://ntpc.youbike.com.tw/cht/index.php'

    def __init__(self, tag, kml_name, meta):
        super(YouBike, self).__init__(tag, meta)
        data = zlib.decompress(
            resource_string('pybikes', 'kml/taiwan.kml.gz'),
            zlib.MAX_WBITS | 16
        )
        kml_tree = etree.fromstring(data)
        city_bounds = kml_tree.xpath("""
            //kml:Placemark[kml:name[text()="%s"]]//kml:coordinates
        """ % kml_name, namespaces=_kml_ns)
        self.city_bounds = map(
            lambda cb: Polygon(
                map(
                    lambda c: tuple(map(float, c.split(','))),
                    filter(None, cb.text.split('\n'))
                )
            ), city_bounds
        )

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper(cache)
        self.stations = map(YouBikeStation, self.get_data(scraper))

    def get_data(self, scraper):
        html = scraper.request(self.main_url)
        data_m = re.search(r'siteContent=\'({.+?})\';', html)
        data = json.loads(data_m.group(1))
        for k, station in data.iteritems():
            lat = float(station['lat'])
            lng = float(station['lng'])
            coord = Point(lng, lat)
            if any(imap(lambda cb: cb.contains(coord), self.city_bounds)):
                yield station


class YouBikeStation(BikeShareStation):
    def __init__(self, data):
        super(YouBikeStation, self).__init__()
        self.name = data['sna']
        self.latitude = float(data['lat'])
        self.longitude = float(data['lng'])
        self.bikes = int(data['sbi'])
        self.free = int(data['bemp'])
        self.extra = {
            'uid': data['sno'],
            'district': data['sarea'],
            'slots': data['tot'],
            'address': data['ar'],
        }
