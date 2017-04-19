# -*- coding: utf-8 -*-
import suds

from .base import BikeShareSystem, BikeShareStation
from . import utils

class Bicicorunha(BikeShareSystem):

    meta = {
        'system': 'bicicorunha',
        'company': ['Empresa Municipal de Vivienda, Servicios y Actividades, S.A.'],
    }

    def __init__(self, tag, meta):
        super(Bicicorunha, self).__init__(tag, meta)
        base_url = 'http://www.bicicoruna.es/wservices/wstatus.asmx?WSDL'
        self.client = BicicorunhaClient(suds.client.Client(base_url))

    def update(self, scraper=None):
        self.stations = self.client.getStations()

class BicicorunhaClient():
    def __init__(self, soap_client):
        self.soap_client=soap_client
    
    def getStations(self):
        stations = []
        for item in self.soap_client.service.GetEstaciones()[0]:
            name = item.Nombre
            latitude = float(item.Latitud)
            longitude = float(item.Longitud)
            bikes = int(item.TotalPuestosOcupados)
            free = int(item.TotalPuestosActivos-item.TotalPuestosOcupados)
            extra = {
                'slots': item.TotalPuestosActivos
            }
            station = BikeShareStation(name, latitude, longitude,
                                       bikes, free, extra)
            stations.append(station)
        
        return stations