# -*- coding: utf-8 -*-
import json

import requests

from . import utils
from .base import BikeShareStation, BikeShareSystem


class BySykkelGraphql(BikeShareSystem):

    authed = False

    meta = {
        'system': 'BySykkelGraphql',
        'company': ['Urban Infrastructure Partner'],
    }

    def __init__(self, tag, meta, feed_url):
        super(BySykkelGraphql, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()
        scraper.headers['Content-Type'] = 'application/json'

        self.stations = []
        query = """
query dockGroups($systemId: ID){
  dockGroups(systemId: $systemId) {
    id
    title
    state
    address
    coord {
      lat
      lng
    }
    docks {
      id
      state
      vehicleDocked
      availabilityState
    }
  }
}
"""

        variables = {'systemId': self.meta['systemId']}

        gql_data = {
            'query': query,
            'operationName': 'dockGroups',
            'variables': variables
        }

        data = json.loads(
            scraper.request(
                self.feed_url,
                data=json.dumps(gql_data).encode('utf-8'),
                method='POST'))

        for info in data['data']['dockGroups']:
            if info['state'] == 'active':
                station = BySykkelGraphqlStation(info)
                self.stations.append(station)


class BySykkelGraphqlStation(BikeShareStation):
    def __init__(self, info):

        super(BySykkelGraphqlStation, self).__init__()

        self.name = info['title']

        self.longitude = float(info['coord']['lng'])
        self.latitude = float(info['coord']['lat'])

        self.bikes = len(
            filter(
                lambda dock: dock['availabilityState'] == 'vehicle_available' or dock['availabilityState'] == 'available',
                info['docks']))
        self.free = len(
            filter(
                lambda dock: dock['availabilityState'] == 'vehicle_available',
                info['docks']))

        self.extra = {
            'id': info['id'],
            'address': info['address'],
        }
