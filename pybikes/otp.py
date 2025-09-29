"""Parser implementation for OpenTripPlanner 2"""

import json

from warnings import warn

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
      byType {
        count
        vehicleType {
          formFactor
          propulsionType
        }
      }
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

        self.stations = [OtpStation(st) for st in data["data"]["vehicleRentalStations"]]
        self.vehicles = [OtpVehicle(vh, self) for vh in data["data"]["rentalVehicles"]]


class OtpStation(BikeShareStation):
    def __init__(self, st):
        extra = {
            "uid": st["stationId"],
            "online": st["operative"],
        }

        if st["capacity"] is not None:
            extra["slots"] = st["capacity"]

        if "rentalUris" in st and st["rentalUris"]:
            extra["rental_uris"] = st["rentalUris"]

        # XXX max int32, meaning always can be dropped, clamp it to 32
        free = st["availableSpaces"]["total"]
        free = 32 if free == 2147483647 else free

        extra.update(self.bike_counts(st))

        super().__init__(
            name=st["name"],
            latitude=st["lat"],
            longitude=st["lon"],
            bikes=st["availableVehicles"]["total"],
            free=free,
            extra=extra,
        )

    def bike_counts(self, data):
        counts = {}
        for vt in data["availableVehicles"]["byType"]:
            # XXX replace with match once py 3.9 dies
            if vt["vehicleType"] == {"formFactor": "BICYCLE", "propulsionType": "HUMAN"}:
                counts.setdefault("normal_bikes", 0)
                counts["normal_bikes"] += vt["count"]

            elif vt["vehicleType"] == {"formFactor": "BICYCLE", "propulsionType": "ELECTRIC_ASSIST"}:
                counts.setdefault("ebikes", 0)
                counts["ebikes"] += vt["count"]

            elif vt["vehicleType"] == {"formFactor": "CARGO_BICYCLE", "propulsionType": "ELECTRIC_ASSIST"}:
                counts.setdefault("ecargo", 0)
                counts["ecargo"] += vt["count"]

            elif vt["vehicleType"] == {"formFactor": "CARGO_BICYCLE", "propulsionType": "HUMAN"}:
                counts.setdefault("cargo", 0)
                counts["cargo"] += vt["count"]
            else:
                warn("Unhandled station vehicle type %s with count %d" %
                     (vt["vehicleType"], vt["count"]))

        return counts


class OtpVehicle(Vehicle):
    def __init__(self, data, system):
        extra = {
            "uid": data["vehicleId"],
            "online": data["operative"],
        }

        if "rentalUris" in data and data["rentalUris"]:
            extra["rental_uris"] = data["rentalUris"]

        if data["fuel"]["percent"]:
            extra["battery"] = float(data["fuel"]["percent"])

        super().__init__(
            latitude=data["lat"],
            longitude=data["lon"],
            extra=extra,
            vehicle_type=self.vehicle_type(data),
            system=system,
        )

    def vehicle_type(self, vehicle):
        # XXX replace with match once py 3.9 dies
        if vehicle["vehicleType"] == {"formFactor": "BICYCLE", "propulsionType": "ELECTRIC_ASSIST"}:
            return VehicleTypes.ebike
        else:
            return VehicleTypes.default
