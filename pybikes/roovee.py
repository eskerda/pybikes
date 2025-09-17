import json
from urllib.parse import urljoin

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.base import Vehicle, VehicleTypes


class Roovee(BikeShareSystem):
    endpoint = "https://api.roovee.eu"

    meta = {"name": "Roovee", "company": ["ROOVEE S.A."]}

    def __init__(self, tag, meta, tenant):
        super().__init__(tag, meta)
        self.tenant = tenant

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        data = scraper.request(**Roovee.bikes_req(self.tenant))
        data = json.loads(data)

        zones = filter(lambda z: z["type"] == "preferredBikeReturnZone", data["zones"])
        self.stations = [RooveeStation(d) for d in zones]
        self.vehicles = [RooveeBike(d, system=self) for d in data["bikes"]]

    @staticmethod
    def zones_req():
        return {"url": urljoin(Roovee.endpoint, "/mobile/zones")}

    @staticmethod
    def bike_types_req():
        return {"url": urljoin(Roovee.endpoint, "/mobile/globalBikeTypes")}

    @staticmethod
    def bikes_req(tenant):
        return {
            "url": urljoin(Roovee.endpoint, "/public/bikesAndZones"),
            "params": {"tenant": tenant},
        }

    @staticmethod
    def bikes_section_req(lat, lng, delta):
        # Returns more information, like internal id and vehicle type id but
        # cannot filter by tenant
        # delta is the "radius". Not precise enough to get a full list of a
        # system without multiple calls
        return {
            "url": urljoin(Roovee.endpoint, "/mobile/bikes/bikesAvailableInSection"),
            "params": {
                "latitude": lat,
                "longitude": lng,
                "LatitudeDelta": delta,
                "LongitudeDelta": delta,
            },
        }


class RooveeStation(BikeShareStation):
    def __init__(self, data):
        super().__init__(
            name=data["name"],
            latitude=data["areaCenter"]["lat"],
            longitude=data["areaCenter"]["lng"],
            bikes=0,
            free=None,
            extra={"virtual": True},
        )


class RooveeBike(Vehicle):
    kind_map = {
        "Standard": VehicleTypes.bicycle,
        "Elektryczny": VehicleTypes.ebike,
        # XXX More types available ...
    }

    def __init__(self, data, system):
        lat = data["location"]["lat"]
        lng = data["location"]["lng"]

        extra = {
            "uid": data["bikeNumber"],
            "online": data["isAvailable"],
        }

        kind = RooveeBike.kind_map.get(data["type"], VehicleTypes.default)

        super().__init__(lat, lng, vehicle_type=kind, extra=extra, system=system)
