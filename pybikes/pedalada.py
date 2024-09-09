import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

STATIONS_URL = '{endpoint}/php/get-stations-details-map.php'
STATION_DETAILS_AND_RIDES_URL = '{endpoint}/php/get-station-details-and-rides.php?n={station_number}'
STATION_IMAGE_URL = '{endpoint}/images/stations/station_{station_number}.jpg'


def station_details_and_rides_url(endpoint, station_number):
    return STATION_DETAILS_AND_RIDES_URL.format(endpoint=endpoint, station_number=station_number)

def station_image_url(endpoint, station_number):
    return STATION_IMAGE_URL.format(endpoint=endpoint, station_number=station_number)

class Pedalada(BikeShareSystem):
    meta = {
        'company': [
            'Share2Go - Mobilidade Partilhada, Sociedade Unipessoal Lda'
        ]
    }

    def __init__(self, tag, meta, endpoint):
        meta['company'] += Pedalada.meta['company']
        super(Pedalada, self).__init__(tag, meta)
        self.endpoint = endpoint

    @property
    def stations_url(self):
        return STATIONS_URL.format(endpoint=self.endpoint)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        stations_data = json.loads(scraper.request(self.stations_url))

        stations = []
        for station in stations_data:
            station = PedaladaStation(station, self.endpoint)
            stations.append(station)

        self.stations = stations

class PedaladaStation(BikeShareStation):
    def __init__(self, data, endpoint):
        super(PedaladaStation, self).__init__()
        self.endpoint = endpoint

        self.name = data['stationName']
        self.latitude = data['latitude']
        self.longitude = data['longitude']

        self.extra = {
            'uid': data['stationNumber'],
            'slots': data['maximumNumberOfRides'],
            'online': data['state'] == 1,
            'photo': station_image_url(endpoint, data['stationNumber']),
            'open': data['stationIsOpen'] == 1,
            'in_maintenance': data['stationInMaintenance'] == 1
        }

        def update(self, scraper=None):
            scraper = scraper or PyBikesScraper()
            station_details_and_rides = scraper.request(station_details_and_rides_url(self.extra['uid']))

            docked_bikes_count = len(station_details_and_rides['rides'])
            self.bikes = docked_bikes_count
            self.free = self.extra['slots'] - docked_bikes_count

            station_details = station_details_and_rides['details'][0]
            self.extra['online'] = station_details['state'] == 1
            self.extra['open'] = station_details['stationIsOpen'] == 1
            self.extra['in_maintenance'] = station_details['stationInMaintenance'] == 1