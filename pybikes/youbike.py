# -*- coding: utf-8 -*-
import re
import json
import zlib
from pkg_resources import resource_string

from lxml import etree

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper, filter_bounds
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
        # Rather ugly way to get the coordinates out of this kml, but its what
        # we have.
        self.city_bounds = []
        for bound in city_bounds:
            coords = filter(None, bound.text.split('\n'))
            # We got the kml with lng / lat
            coords = map(lambda c: reversed(c.split(',')), coords)
            coords = map(lambda ll: map(float, ll), coords)
            self.city_bounds.append(coords)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper(cache)
        html = scraper.request(self.main_url)
        data_m = re.search(r'siteContent=\'({.+?})\';', html)
        data = json.loads(data_m.group(1))
        filtered_data = filter_bounds(
            data.itervalues(),
            lambda s: (float(s['lat']), float(s['lng'])),
            * self.city_bounds
        )
        self.stations = list(map(YouBikeStation, filtered_data))


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
