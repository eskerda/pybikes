# -*- coding: utf-8 -*-
import json

from . import utils
from .base import BikeShareStation, BikeShareSystem

BYSYKKEL_GRAPHQL_URL = "https://core.urbansharing.com/public/api/v1/graphql"


class BysykkelGraphql(BikeShareSystem):

    authed = False

    meta = {
        'system': 'Bysykkel GraphQL',
        'company': ['Urban Infrastructure Partner'],
    }

    def __init__(self, tag, meta, systemId):
        super(BysykkelGraphql, self).__init__(tag, meta)
        self.systemId = systemId

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
      availabilityState
    }
  }
}
"""

        variables = {'systemId': self.systemId}

        gql_data = {
            'query': query,
            'operationName': 'dockGroups',
            'variables': variables
        }

        data = json.loads(
            scraper.request(
                BYSYKKEL_GRAPHQL_URL,
                data=json.dumps(gql_data).encode('utf-8'),
                method='POST'))

        for info in data['data']['dockGroups']:
            if info['state'] == 'active':
                station = BysykkelGraphqlStation(info)
                self.stations.append(station)


class BysykkelGraphqlStation(BikeShareStation):
    def __init__(self, info):

        super(BysykkelGraphqlStation, self).__init__()

        self.name = info['title']

        self.longitude = float(info['coord']['lng'])
        self.latitude = float(info['coord']['lat'])

        self.free = len(
            filter(lambda dock: dock['availabilityState'] == 'available',
                   info['docks']))
        self.bikes = len(
            filter(
                lambda dock: dock['availabilityState'] == 'vehicle_available',
                info['docks']))

        self.extra = {
            'uid': info['id'],
            'address': info['address'],
            'slots': len(info['docks']),
        }
