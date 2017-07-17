# -*- coding: utf-8 -*-
import json

from .base import BikeShareSystem, BikeShareStation
from . import utils


class BySykkel(BikeShareSystem):

    meta = {
        'system': 'BySykkel',
        'company': ['Urban Infrastructure Partner']
    }

    def __init__(self, tag, meta, feed_url, feed_details_url, feed_token):
        super(BySykkel, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.feed_details_url = feed_details_url
        self.feed_token = feed_token

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
            scraper.setUserAgent("pybikes - github.com/eskerda/pybikes/tree/master/pybikes")
            scraper.headers['Client-Identifier'] = self.feed_token

        stations = []
        details = []

        stations_data = json.loads(scraper.request(self.feed_url))
        details_data = json.loads(scraper.request(self.feed_details_url))

        '''
        stations_data
            {
                "stations": [{
                    "id": 178,
                    "title": "Colosseum Kino",
                    "subtitle": "langs Fridtjof Nansens vei",
                    "ready": true,
                    "center": {
                        "latitude": 59.929838,
                        "longitude": 10.711223
                    }
                }, ...
            }
            
            details_data
            {
                "stations": [{
                    "id": 8,
                    "availability": {
                        "bikes": 13,
                        "locks": 5
                    }
                }, ...
                ],
                    "updated_at": "2017-07-17T19:56:44+00:00",
                    "refresh_rate": 10.0
                }                
            
        '''




        for item in stations_data['stations']:
            station = BikeShareStation()

            station.name = item['title']

            station.longitude = float(item['center']['longitude'])
            station.latitude  = float(item['center']['latitude'])

            details_filtered = [obj for obj in details_data['stations'] if(obj['id'] == item['id'])]
            #for stationdetails in details_data['stations']:
            #    if(stationdetails['id'] == item['id']):


            #print(details_filtered[0]['availability'])

            station.bikes = details_filtered[0]['availability']['locks'] + details_filtered[0]['availability']['bikes']
            station.free = details_filtered[0]['availability']['bikes']
            station.extra = {
                'slots':  details_filtered[0]['availability']['locks'],
                'uid': item['id']
            }

            stations.append(station)

        self.stations = stations
