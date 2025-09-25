"""Parser implementation for OpenTripPlanner 2"""

import json

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.base import Vehicle, VehicleTypes

BLERGH_QUERY = """
query {
  rentalVehicles {
    allowPickupNow
    availableUntil
    fuel {
      percent
      range
    }
    id
    lat
    lon
    name
    operative
    rentalNetwork {
      networkId
      url
    }
    rentalUris {
      android
      ios
      web
    }
    vehicleId
    vehicleType {
      formFactor
      propulsionType
    }
  }

  vehicleRentalStations {
    allowDropoff
    allowDropoffNow
    allowOverloading
    allowPickup
    allowPickupNow
    availableSpaces {
      total
    }
    availableVehicles {
      total
    }
    capacity
    id
    lat
    lon
    name
    operative
    realtime
    rentalNetwork {
      networkId
      url
    }
    rentalUris {
      android
      ios
      web
    }
    stationId
  }
}
"""


class OTP(BikeShareSystem):
    def __init__(self, tag, meta, feed_url, bbox=None):
        super(OTP, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.bbox = bbox

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        headers = {"content-type": "application/json"}
        payload = {"query": BLERGH_QUERY, "variables": {}}

        data = scraper.request(
            self.feed_url,
            method="POST",
            data=json.dumps(payload),
            headers=headers,
        )
        data = json.loads(data)

        self.stations = [
            BikeShareStation(
                name=st["name"],
                latitude=st["lat"],
                longitude=st["lon"],
                bikes=st["availableVehicles"]["total"],
                free=st["availableSpaces"]["total"],
                extra={
                    "uid": st["id"],
                    "online": st["operative"],
                },
            )
            for st in data["data"]["vehicleRentalStations"]
        ]

        self.vehicles = [
            Vehicle(
                latitude=vh["lat"],
                longitude=vh["lon"],
                extra={},
                system=self,
            ) for vh in data["data"]["rentalVehicles"]
        ]
