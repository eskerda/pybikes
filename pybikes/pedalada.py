import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

STATIONS_URL = '{endpoint}/php/get-stations-details-map.php'
STATION_DETAILS_URL = '{endpoint}/php/get-station-details-and-rides.php?n={station_number}'
STATION_IMAGE_URL = '{endpoint}/images/stations/station_{station_number}.jpg'


def station_details_url(endpoint, station_number):
    return STATION_DETAILS_URL.format(endpoint=endpoint, station_number=station_number)

def station_image_url(endpoint, station_number):
    return STATION_DETAILS_URL.format(endpoint=endpoint, station_number=station_number)

class Pedalada(BikeShareSystem):
    meta = {
        'company': [
            'Share2Go - Mobilidade Partilhada, Sociedade Unipessoal Lda'
        ]
    }

    def __init__(self, tag, meta, endpoint, bbox=None):
        meta['company'] += Pedalada.meta['company']
        super(Pedalada, self).__init__(tag, meta, bounds=bbox)
        self.endpoint = endpoint

    @property
    def stations_url(self):
        return STATIONS_URL.format(endpoint=self.endpoint)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        stations_data = json.loads(scraper.request(self.stations_url))

        stations = []
        for station in stations_data:
            station_details = scraper.request(station_details_url(station['stationNumber']))
            station = PedaladaStation(station, station_details, self.endpoint)
            stations.append(station)

        self.stations = stations


class PedaladaStation(BikeShareStation):
    def __init__(self, station, station_details, endpoint):
        super(PedaladaStation, self).__init__()
        self.endpoint = endpoint

        self.name = station['stationName']
        self.latitude = station['latitude']
        self.longitude = station['longitude']

        docked_bikes_count = len(station_details['rides'])
        self.bikes = docked_bikes_count
        self.free = station['maximumNumberOfRides'] - docked_bikes_count

        self.extra = {
            'uid': station['stationNumber'],
            'slots': station['maximumNumberOfRides'],
            'online': station['state'] == 1,
            'photo': station_image_url(endpoint, station['stationNumber'])
        }