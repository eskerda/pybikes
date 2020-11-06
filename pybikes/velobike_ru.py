# -*- coding: utf-8 -*-
import json
import re

from .base import BikeShareSystem, BikeShareStation
from . import utils


class VelobikeRU(BikeShareSystem):

    sync = True

    meta = {
        'system': 'Velobike RU',
        'company': ['ЗАО «СитиБайк»']
    }

    def __init__(self, tag, feed_url, meta):
        super(VelobikeRU, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        stations = []

        data = json.loads(scraper.request(self.feed_url))

        #Each station is
        #{
        #  "StationTypes":[
        #    "electric",
        #    "ordinary"
        #  ],
        #  "TotalOrdinaryPlaces":42,
        #  "IconsSet":2,
        #  "AvailableOrdinaryBikes":48,
        #  "FreeElectricPlaces":1,
        #  "FreeOrdinaryPlaces":5,
        #  "IsFavourite":false,
        #  "TotalPlaces":66,
        #  "HasTerminal":false,
        #  "Position": {
        #    "Lat":55.7351049,
        #    "Lon":37.5937289
        # },
        #  "Address":"\u0417\u0443\u0431\u043e\u0432\u0441\u043a\u0438\u0439 \u0431-\u0440, \u0434.5, \u0441\u0442\u0440.1 (\u0441\u0442. \u043c. \u041f\u0430\u0440\u043a \u041a\u0443\u043b\u044c\u0442\u0443\u0440\u044b)",
        #  "AvailableElectricBikes":16,
        #  "Id":"0100",
        #  "TotalElectricPlaces":24,
        #  "TemplateId":6,
        #  "IsLocked":true,
        #  "FreePlaces":6,
        #  "Name":""
        #}
        for item in data['Items']:
            name = item['Address']
            latitude = float(item['Position']['Lat'])
            longitude = float(item['Position']['Lon'])
            bikes = int(item['AvailableOrdinaryBikes'])+int(item['AvailableElectricBikes'])
            free = int(item['FreePlaces'])
            extra = {
                'uid': item['Id'],
                'slots': int(item['TotalPlaces']),
                'address': re.sub(r'^\d+\s*-\s*', '', item['Address']),
                'normal_slots': int(item['TotalOrdinaryPlaces']),
                'electric_slots': int(item['TotalElectricPlaces']),
                'normal_bikes': int(item['AvailableOrdinaryBikes']),
                'ebikes': int(item['AvailableElectricBikes']),
                'normal_free': int(item['FreeOrdinaryPlaces']),
                'electric_free': int(item['FreeElectricPlaces'])
            }
            if 'electric' in item['StationTypes']:
                extra['has_ebikes'] = True
            station = BikeShareStation(name, latitude, longitude, bikes, free, extra)
            stations.append(station)
        self.stations = stations
