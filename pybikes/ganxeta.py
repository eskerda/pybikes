# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

ENDPOINT = "https://bks-api.ganxeta.cat/rms-bike-sharing-real-time/graphql"


class Ganxeta(BikeShareSystem):
    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }

    payload = {
        "operationName": "StationsRealtime",
        "query": """query StationsRealtime {
            get_data_real_time { 
                station_id
                station_state_id
                station_name
                station_address
                latitude
                longitude
                bikes_total
                bikes_available
                bikes_reserved
                bikes_maintenance
                bikes_occupancy_status
                bikes_occupancy_color
                racks_total
                racks_available
                racks_broken
                racks_occupancy_status
                racks_occupancy_color
                station_external_id
            }
        }""",
    }

    def __init__(self, tag, meta):
        super(Ganxeta, self).__init__(tag, meta)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = scraper.request(
            ENDPOINT,
            data=json.dumps(Ganxeta.payload),
            headers=Ganxeta.headers,
            method="POST",
        )
        data = json.loads(data)

        stations = []

        for station in data["data"]["get_data_real_time"]:
            stations.append(GanxetaStation(station))

        self.stations = stations


class GanxetaStation(BikeShareStation):
    def __init__(self, data):
        super(GanxetaStation, self).__init__()
        self.name = data["station_name"]
        self.latitude = float(data["latitude"])
        self.longitude = float(data["longitude"])

        self.bikes = int(data["bikes_available"])
        self.free = int(data["racks_available"])

        self.extra = {
            "uid": data["station_id"],
            "address": data["station_address"],
            "slots": int(data["racks_total"]),
            "number": data["station_external_id"],
        }
