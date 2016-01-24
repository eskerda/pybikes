# -*- coding: utf-8 -*-
import re

from .base import BikeShareSystem, BikeShareStation
from . import utils


class Movete(BikeShareSystem):

    meta = {
        'system': 'Movete',
        'company': ['Sistema de Transporte Metropolitano',
                    'Intendencia de Montevideo']
    }

    url = 'http://movete.montevideo.gub.uy/index.php?option=com_content&view=article&id=1&Itemid=2'  # NOQA

    def update(self, scraper=None):
        if scraper is None:
            scraper = utils.PyBikesScraper()

        self.stations = []
        data = scraper.request(self.url)
        station_list_m = re.search(r'var paradas\s*=\s*(\[.+\]);', data,
                                   flags=re.DOTALL)
        if not station_list_m:
            return

        station_list = re.findall(r'\[\'.+?\'\]', station_list_m.group(1))
        for data in station_list:
            data = eval(data)
            if int(data[4]) == -1:
                # Office marker
                continue
            name = data[0]
            latitude = float(data[1])
            longitude = float(data[2])
            bikes = int(data[6])
            slots = int(data[7])
            free = slots - bikes
            number = next(iter(re.findall(r'(\d+)', name)), None)
            extra = {
                'slots': slots,
                'uid': data[3],
                'number': number
            }

            station = BikeShareStation(name, latitude, longitude, bikes, free,
                                       extra)
            self.stations.append(station)
