# -*- coding: utf-8 -*-
# Copyright (C) 2026, Martín González Gómez <m@martingonzalez.net>

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper

ENDPOINT = "https://charichari.bike/api/graphql"


class Charichari(BikeShareSystem):
    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }
    meta = {
        'system': 'Charichari',
        'company': [
            'Charichari, Inc'
        ]
    }

    def __init__(self, tag, region_id, meta):
        super(Charichari, self).__init__(tag, meta)
        self.region_id = region_id

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        payload = {
            "operationName": "listPorts",
            "query": """query listPorts($regionId: String!) {
                ports(regionId: $regionId) {
                    id
                    title
                    address
                    capacity
                    location {
                        latitude
                        longitude
                    }
                }
            }""",
            "variables": {
                "regionId": self.region_id
            }
        }

        data = scraper.request(
            ENDPOINT,
            data=json.dumps(payload),
            headers=Charichari.headers,
            method="POST",
        )
        data = json.loads(data)

        stations = []

        for station in data["data"]["ports"]:
            stations.append(CharichariStation(station))

        self.stations = stations


class CharichariStation(BikeShareStation):
    def __init__(self, data):
        super(CharichariStation, self).__init__()
        self.name = data["title"]
        self.latitude = float(data["location"]["latitude"])
        self.longitude = float(data["location"]["longitude"])

        # only dock information available
        self.bikes = 0
        self.free = int(data["capacity"])

        self.extra = {
            "uid": data["id"],
            "address": data["address"]
        }
