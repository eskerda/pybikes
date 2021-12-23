# -*- coding: utf-8 -*-

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


class VelokSystem(BikeShareSystem):

    meta = {
        'system': 'Velok',
        'company': ['CIGL ESCH'],
        'source': 'https://docs.api.tfl.lu/v1/en/RESTAPIs/BikePoint/',
        'ebikes': True,
    }

    feed_url = "https://api.tfl.lu/v1/BikePoint"

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(VelokSystem.feed_url))
        self.stations = [
            VelokStation(f) for f in data['features']
                if 'velok' in f['properties']['id']
        ]


class VelokStation(BikeShareStation):
    def __init__(self, data):
        """
          {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [5.98276, 49.49473]
            },
            "properties": {
                "id": "velok:1",
                "open": true,
                "name": "Avenue de la Gare",
                "city": "Esch-sur-Alzette",
                "address": "Coin Rue de l’Alzette",
                "photo": "https://webservice.velok.lu/images/photos/1.jpg",
                "docks": 7,
                "available_bikes": 4,
                "available_ebikes": 0,
                "available_docks": 3,
                "last_update": null,
                "dock_status": [{
                    "status": "occupied",
                    "bikeType": "manual"
                }, {
                    "status": "free",
                    "bikeType": null
                }, {
                    "status": "occupied",
                    "bikeType": "manual"
                }, {
                    "status": "free",
                    "bikeType": null
                }, {
                    "status": "occupied",
                    "bikeType": "manual"
                }, {
                    "status": "free",
                    "bikeType": null
                }, {
                    "status": "occupied",
                    "bikeType": "manual"
                }]
            }
          }
        """

        props = data['properties']
        name = props['name']
        longitude, latitude = map(float, data['geometry']['coordinates'])
        bikes = props['available_bikes'] + props['available_ebikes']
        free = props['available_docks']

        extra = {
            'uid': props['id'].split(':')[-1],
            'address': props['address'],
            'photo': props['photo'],
            'slots': props['docks'],
            'online': props['open'],
            'ebikes': props['available_ebikes'],
        }

        super(VelokStation, self).__init__(name=name, latitude=latitude,
            longitude=longitude, bikes=bikes, free=free, extra=extra)
