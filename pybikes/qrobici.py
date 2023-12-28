# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

FEED_URL = "https://qrobici.mx/mobile/getStations"


class QroBici(BikeShareSystem):
    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(FEED_URL, ssl_verification=False))

        stations = []

        for station in data["estaciones"]:
            stations.append(QroBiciStation(station))

        self.stations = stations


class QroBiciStation(BikeShareStation):
    def __init__(self, data):
        super(QroBiciStation, self).__init__()

        self.name = data["T_NOMBRE"]
        self.latitude = float(data["T_LATITUD"])
        self.longitude = float(data["T_LONGITUD"])

        self.bikes = int(data["BICICLETAS_DISPONIBLES"])
        self.free = int(data["ESPACIOS_DISPONIBLES"])

        self.extra = {
            "uid": data["id"],
            "address": data["T_REFERENCIA"],
            "slots": data["E_NO_SLOTS"],
            "status": data["ESTATUS"],
            "online": data["ESTATUS"] == "En línea",
            "last_update": data["FH_FECHA_ULTIMA_CONEXION"],
        }
