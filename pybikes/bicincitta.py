# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt

import re

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

        raw_lat   = re.findall(BicincittaOld._RE_INFO_LAT_CORD,data);
        raw_lng   = re.findall(BicincittaOld._RE_INFO_LNG_CORD,data);
        raw_name  = re.findall(BicincittaOld._RE_INFO_NAME,data);
        raw_avail = re.findall(BicincittaOld._RE_INFO_AVAIL,data);

        vec_lat   = BicincittaOld._clean_raw(raw_lat[0]);
        vec_lng   = BicincittaOld._clean_raw(raw_lng[0]);
        vec_name  = BicincittaOld._clean_raw(raw_name[0]);
        vec_avail = BicincittaOld._clean_raw(raw_avail[0]);
        
        stations = []

        for index, name in enumerate(vec_name):
            latitude    = float(vec_lat[index])
            longitude   = float(vec_lng[index])
            description = None
            bikes       = int(vec_avail[index].count('4'))
            free        = int(vec_avail[index].count('0'))
            station     = BicincittaStation(index, name, description, \
                            latitude, longitude, bikes, free)
            stations.append(station)
        self.stations = stations

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
            self.system_id = system_id
            self.url = [endpoint.format(id = system_id)]
        elif 'comunes' in instance:
            self.url = map(
                lambda comune: endpoint.format(id = comune['id']),
                instance['comunes']
            )
        else:
            self.url = [endpoint]


    def update(self, scraper = None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        self.stations = []
        for url in self.url:
            self.stations += Bicincitta._getStations(url, scraper)

    @staticmethod
    def _getStations(url, scraper):
        data = scraper.request(url)
        raw  = re.findall(Bicincitta._RE_INFO, data)
        info = raw[0].split('\',\'')
        info = map(lambda chunk: chunk.split('|'), info)
        stations = []

        for index in range(len(info[0])):
            name        = info[5][index]
            description = info[7][index]
            latitude    = float(info[3][index])
            longitude   = float(info[4][index])
            bikes       = int(info[6][index].count('4'))
            free        = int(info[6][index].count('0'))
            station     = BicincittaStation(index, name, description, \
                            latitude, longitude, bikes, free)
            stations.append(station)
        return stations

class BicincittaStation(BikeShareStation):
    def __init__(self, id, name, description, lat, lng, bikes, free):
        super(BicincittaStation, self).__init__(id)

        if name[-1] == ":":
            name = name[:-1]

        self.name        = utils.clean_string(name)
        self.latitude    = lat
        self.longitude   = lng
        self.bikes       = bikes
        self.free        = free
        self.extra       = { }

        if description is not None and description != u'':
            self.extra['description'] = utils.clean_string(description)

