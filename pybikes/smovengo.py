# -*- coding: utf-8 -*-
# Copyright (C) 2016, Lluis Esquerda <eskerda@gmail.com>
# Copyright (C) 2015, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class Smovengo(BikeShareSystem):
    sync = True

    meta = {
        'system': 'Smovengo',
        'company': ['Smovengo']
    }

    def __init__(self, tag, api_url, meta):
        self.api_url = api_url
        super(Smovengo, self).__init__(tag, meta)

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        stations_data = json.loads(scraper.request(self.api_url))

        stations = []
        for station_data in stations_data:
            try:
                int(station_data["station"]["code"])
            except ValueError:
                # Skip any station whose "code" is not an int. Sometimes, some
                # stations have weird code such as "Zzz delete me" and are
                # obviously not real stations.
                # Station code in Paris is always a number and two first digits
                # represent the borough number.
                continue

            name = station_data["station"]["name"]
            latitude = station_data["station"]["gps"]["latitude"]
            longitude = station_data["station"]["gps"]["longitude"]

            manual_bikes = station_data["nbBike"]
            electric_bikes = station_data["nbEbike"]
            bikes = manual_bikes + electric_bikes

            free = station_data["nbFreeDock"] + station_data["nbFreeEDock"]

            extra = {
                "uid": station_data["station"]["code"],
                "status": station_data["station"]["state"],
                "banking": station_data["creditCard"] != "no",
                "dueDate": station_data["station"]["dueDate"],
                "slots": station_data["nbDock"] + station_data["nbEDock"],
                "bikes_overflow": station_data["nbBikeOverflow"],
                "ebikes_overflow": station_data["nbEBikeOverflow"],
                "has_ebikes": station_data["nbEbike"] > 0,
                "ebikes": station_data["nbEbike"],
                "online": station_data["station"]["state"].lower() == "operative"
            }
            station = BikeShareStation(name, float(latitude), float(longitude),
                                       int(bikes), int(free), extra)
            stations.append(station)
        self.stations = stations
