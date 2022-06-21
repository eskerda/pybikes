# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import json

import lxml.html

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class IDEcycle(BikeShareSystem):
    def __init__(self, tag, meta, feed_url):
        super(IDEcycle, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        html = scraper.request(self.feed_url)
        geoj = re.findall(r'var geojsondatas = (.*?);', html, flags=re.DOTALL)
        data = json.loads(geoj[0])
        self.stations = [ IDEcycleStation(feature) for feature in data['features'] ]


class IDEcycleStation(BikeShareStation):
    def __init__(self, fields):
        name = fields['properties']['title']
        latitude = fields['geometry']['coordinates'][1]
        longitude = fields['geometry']['coordinates'][0]

        raw = fields['properties']['popupContent']
        popup = lxml.html.fromstring(raw)
        text = " ".join(popup.xpath("//text()"))
        addressRGX = u"<p>(.*?)</br>"

        free = int(re.findall(u'(\d+) Places libres', text, re.UNICODE)[0])
        bikes = int(re.findall(u'(\d+) Vélos disponibles', text, re.UNICODE)[0])

        extra = {
            'uid': popup.xpath("//a/@data-poi")[0],
            'address': re.findall(addressRGX, raw, re.UNICODE)[0],
            'slots': int(re.findall(u'Capacité : (\d+) vélos', text, re.UNICODE)[0]),
            # All current stations (17) have a payment card reader
            # See the data here: https://data.idelis.fr/explore/dataset/stations-velo-en-libre-service-idecycle/table/
            'payment-terminal': True,
        }
        super(IDEcycleStation, self).__init__(name, latitude, longitude, bikes, free, extra)


class KeolisIlevia(BikeShareSystem):

    meta = {
        'system': 'Keolis',
        'company': ['Keolis'],
    }

    # Rows: -1 gives us all the results without the need to paginate
    BASE_URL = "https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset={dataset}&rows=-1"     # NOQA

    def __init__(self, tag, dataset, meta):
        super(KeolisIlevia, self).__init__(tag, meta)
        self.feed_url = KeolisIlevia.BASE_URL.format(dataset=dataset)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.feed_url))
        records = map(lambda r: r['fields'], data['records'])
        self.stations = list(map(KeolisIleviaStation, records))


class KeolisIleviaStation(BikeShareStation):
    def __init__(self, fields):
        name = fields['nom']
        latitude, longitude = map(float, fields['localisation'])
        bikes = int(fields['nbvelosdispo'])
        free = int(fields['nbplacesdispo'])
        extra = {
            'status': fields['etat'],
            'uid': str(fields['libelle']),
            'city': fields['commune'],
            'address': fields['adresse'],
            'last_update': fields['datemiseajour'],
            'online': fields['etat'] == 'EN SERVICE',
            'payment-terminal': fields['type'] == 'AVEC TPE',
        }
        super(KeolisIleviaStation, self).__init__(name, latitude, longitude,
                                                bikes, free, extra)

class KeolisSTAR(BikeShareSystem):

    meta = {
        'system': 'Keolis',
        'company': ['Keolis'],
    }

    # Rows: -1 gives us all the results without the need to paginate
    BASE_URL = "https://data.explore.star.fr/api/records/1.0/search/?dataset={dataset}&rows=-1"     # NOQA

    def __init__(self, tag, dataset, meta):
        super(KeolisSTAR, self).__init__(tag, meta)
        self.feed_url = KeolisSTAR.BASE_URL.format(dataset=dataset)
        self.meta['source'] = self.meta['source'].format(dataset=dataset)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.feed_url))
        records = map(lambda r: r['fields'], data['records'])
        self.stations = list(map(KeolisSTARStation, records))


class KeolisSTARStation(BikeShareStation):
    def __init__(self, fields):
        name = fields['nom']
        latitude, longitude = map(float, fields['coordonnees'])
        bikes = int(fields['nombrevelosdisponibles'])
        free = int(fields['nombreemplacementsdisponibles'])
        extra = {
            'slots': fields['nombreemplacementsactuels'],
            'status': fields['etat'],
            'uid': str(fields['idstation']),
            'last_update': fields['lastupdate'],
            'online': fields['etat'] == 'En fonctionnement',
            # https://data.rennesmetropole.fr/explore/dataset/stations_vls/api/
            'payment-terminal': True,
        }
        super(KeolisSTARStation, self).__init__(name, latitude, longitude,
                                                bikes, free, extra)


class VCub(BikeShareSystem):

    meta = {
        'system': 'Keolis',
        'company': ['Keolis'],
        'ebikes': True,
    }

    def __init__(self, tag, meta, feed_url):
        super(VCub, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.feed_url))

        self.stations = list(map(VCubStation, data['lists']))


class VCubStation(BikeShareStation):
    def __init__(self, fields):
        super(VCubStation, self).__init__()
        self.name = fields['name']
        self.latitude = float(fields['latitude'])
        self.longitude = float(fields['longitude'])

        ebikes = int(fields['nbElectricBikeAvailable'])
        manual_bikes = int(fields['nbBikeAvailable'])

        self.bikes = ebikes + manual_bikes
        self.free = int(fields['nbPlaceAvailable'])

        self.extra = {
            'uid': str(fields['id']),
            'last_update': fields['updatedAt'],
            'address': fields['address'],
            'city': fields['city'],
            'online': fields['connexionState'] == 'CONNECTEE',
            'slots': self.bikes + self.free,
            'ebikes': ebikes,
            'normal_bikes': manual_bikes,
            'has_ebikes': 'nbElectricBikeAvailable' in fields,
        }
