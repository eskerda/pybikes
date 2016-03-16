# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import re
import HTMLParser

from .base import BikeShareSystem, BikeShareStation
from . import utils

__all__ = ['BicincittaOld', 'Bicincitta','BicincittaStation']

class BaseSystem(BikeShareSystem):
    meta = {
        'system': 'Bicincittà',
        'company': 'Comunicare S.r.l.'
    }

class BicincittaOld(BaseSystem):
    sync = True
    _useragent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:14.0) '\
                 'Gecko/20100101 Firefox/14.0.1'
    _RE_INFO_LAT_CORD = "var sita_x =(.*?);"
    _RE_INFO_LNG_CORD = "var sita_y =(.*?);"
    _RE_INFO_NAME     = "var sita_n =(.*?);"
    _RE_INFO_AVAIL    = "var sita_b =(.*?);"
    _endpoint         = "http://www.bicincitta.com/citta_v3.asp?id={id}&pag=2"

    def __init__(self, tag, meta, system_id):
        super(BicincittaOld, self).__init__(tag, meta)
        self.system_id = system_id
        self.url = BicincittaOld._endpoint.format(id = system_id)

    @staticmethod
    def _clean_raw(raw_string):
        raw_string = raw_string.strip()
        raw_string = raw_string.replace("+","")
        raw_string = raw_string.replace("\"","")
        return raw_string.split("_")

    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.setUserAgent(BicincittaOld._useragent)

        data = scraper.request(self.url)
        data = HTMLParser.HTMLParser().unescape(data)

        raw_lat   = re.findall(BicincittaOld._RE_INFO_LAT_CORD,data);
        raw_lng   = re.findall(BicincittaOld._RE_INFO_LNG_CORD,data);
        raw_name  = re.findall(BicincittaOld._RE_INFO_NAME,data);
        raw_avail = re.findall(BicincittaOld._RE_INFO_AVAIL,data);

        vec_lat   = BicincittaOld._clean_raw(raw_lat[0]);
        vec_lng   = BicincittaOld._clean_raw(raw_lng[0]);
        vec_name  = BicincittaOld._clean_raw(raw_name[0]);
        vec_avail = BicincittaOld._clean_raw(raw_avail[0]);

        self.stations = [
            BicincittaStation (
                name, None, lat, lng, avail.count('4'), avail.count('0')
            ) for name, lat, lng, avail in zip(
                vec_name, vec_lat, vec_lng, vec_avail
            )
        ]

class Bicincitta(BaseSystem):
    sync = True
    _RE_INFO="RefreshMap\((.*?)\)\;"
    _endpoint = "http://bicincitta.tobike.it/frmLeStazioni.aspx?ID={id}"

    def __init__(self, tag, meta, ** instance):
        super(Bicincitta, self).__init__(tag, meta)

        if 'endpoint' in instance:
            endpoint = instance['endpoint']
        else:
            endpoint = Bicincitta._endpoint

        if 'system_id' in instance:
            self.system_id = instance['system_id']
            self.url = [endpoint.format(id=self.system_id)]
        elif 'comunes' in instance:
            self.url = map(
                lambda comune: endpoint.format(id=comune['id']),
                instance['comunes']
            )
        else:
            self.url = [endpoint]

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        self.stations = []
        for url in self.url:
            stations = Bicincitta._getComuneStations(url, scraper)
            self.stations += stations

    @staticmethod
    def _getComuneStations(url, scraper):
        data = scraper.request(url)
        raw = re.findall(Bicincitta._RE_INFO, data)
        info = raw[0].split('\',\'')
        info = map(lambda chunk: chunk.split('|'), info)
        # Yes, this is a joke
        return [BicincittaStation(name, desc, float(lat), float(lng),
                stat.count('4'), stat.count('0')) for name, desc, lat, lng,
                stat in zip(info[5], info[7], info[3], info[4], info[6])]


class BicincittaStation(BikeShareStation):
    def __init__(self, name, description, lat, lng, bikes, free):
        super(BicincittaStation, self).__init__()

        if name[-1] == ":":
            name = name[:-1]

        # There's a bug that sometimes will give lat / lngs on 1E6
        # http://www.tobike.it/frmLeStazioni.aspx?ID=22
        # search for (7676168)
        lat = float(lat)
        lng = float(lng)
        if lat > 85.0 or lat < -85.0:
            lat = lat / 1E6
        if lng > 180.0 or lng < -180.0:
            lng = lng / 1E6

        self.name        = utils.clean_string(name)
        self.latitude    = lat
        self.longitude   = lng
        self.bikes       = int(bikes)
        self.free        = int(free)
        self.extra       = { }

        if description:
            self.extra['description'] = utils \
                    .clean_string(description) \
                    .rstrip(' :')

