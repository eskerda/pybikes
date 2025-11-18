import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.base import Vehicle, VehicleTypes


class SYSTEM_CLASS(BikeShareSystem):

    meta = {
        # Name of the company behind the system
        "company": ["Some company name"],
        # XXX add license if it applies
        "license": {
            "name": "Name of the license",
            "url": "https://link.to.license.example"
        }
    }

    def __init__(self, tag, meta, endpoint):
        super().__init__(tag, meta)
        self.endpoint = endpoint

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = scraper.request(self.endpoint)
        data = json.loads(data)

        # XXX remove if system does not support stations
        self.stations = [
            BikeShareStation(
                name=st["name"],
                latitude=st["latitude"],
                longitude=st["longitude"],
                bikes=st["bikes"],
                free=st["free"],
                # Add more extra fields if available
                extra={
                    "uid": st["id"],
                    "online": st["online"],
                },
            ) for st in data["stations"]
        ]

        # XXX remove if system does not support vehicles
        self.vehicles = [
            Vehicle(
                latitude=vh["latitude"],
                longitude=vh["longitude"],
                system=self,
                vehicle_type=getattr(VehicleTypes, vh["type"]),
                extra={
                    "uid": vh["id"],
                    "online": vh["online"],
                }
            ) for vh in data["vehicles"]
        ]
