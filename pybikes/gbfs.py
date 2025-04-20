# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

# XXX: break this parser into different implementations for GBFS 2 and 3
# it's a mess as it is

import json
from warnings import warn
from urllib.parse import urljoin, urlparse, parse_qs

from pybikes import BikeShareSystem, BikeShareStation, exceptions
from pybikes.utils import PyBikesScraper, filter_bounds
from pybikes.base import Vehicle, VehicleTypes


def get_text(text):
    if isinstance(text, str):
        return text
    if isinstance(text, list):
        return next(iter(text))['text']
    return None


class Gbfs(BikeShareSystem):

    station_cls = None

    def __init__(
        self,
        tag,
        meta,
        feed_url,
        force_https=False,
        station_information=False,
        station_status=False,
        vehicle_types=False,
        free_bike_status=False,
        ignore_errors=False,
        retry=None,
        bbox=None,
        region_id=None,
        append_feed_args_to_req=False,
    ):
        # Add feed_url to meta in order to be exposed to the API
        meta['gbfs_href'] = feed_url
        super(Gbfs, self).__init__(tag, meta)
        self.feed_url = feed_url
        self.force_https = force_https
        self.ignore_errors = ignore_errors
        self.retry = retry
        self.bbox = bbox
        self.region_id = region_id

        if append_feed_args_to_req:
            purl = urlparse(feed_url)
            self.req_args = parse_qs(purl.query)
        else:
            self.req_args = {}

        # Allow hardcoding feed urls on initialization
        self.feeds = {}
        if station_information:
            self.feeds['station_information'] = station_information

        if station_status:
            self.feeds['station_status'] = station_status

        if vehicle_types:
            self.feeds['vehicle_types'] = vehicle_types

        if free_bike_status:
            self.feeds['free_bike_status'] = free_bike_status

    @property
    def default_feeds(self):
        url = self.feed_url
        return {
            "station_information": urljoin(url, 'station_information.json'),
            "station_status": urljoin(url, 'station_status.json'),
        }

    def resolve_vehicles(self, vehicle_info):
        def snoop(s, v, i):
            warn("Unhandled station vehicle type %s with count %d" % (i, v['count']))

        def vnoop(s, v, i):
            raise exceptions.UnhandledVehicleException("unhandled vehicle type %s" % (i))

        resolvers = {}
        for v in vehicle_info['data'].get('vehicle_types', []):
            sr, vr = next(iter(((sr, vr) for q, sr, vr in self.vehicle_taxonomy if q(v))), (snoop, vnoop))
            vid = v.get('vehicle_type_id', 'err')
            resolvers[vid] = (v, sr or snoop, vr or vnoop)

        return resolvers


    # XXX Move this to Station, since Vehicle will have its own taxonomy
    @property
    def vehicle_taxonomy(self):

        # contains pairs of (vehicle query, resolver)
        return [
            (
                lambda v: 'propulsion_type' in v and v['propulsion_type'] == 'human' and v['form_factor'] == 'bicycle',
                GbfsStation.update_normal_bikes,
                GbfsVehicle.update_normal_bikes,
            ),
            (
                lambda v: 'propulsion_type' in v and v['propulsion_type'] in ['electric_assist', 'electric'] and v['form_factor'] == 'bicycle',
                GbfsStation.update_ebikes,
                GbfsVehicle.update_ebikes,
            ),
            (
                lambda v: 'propulsion_type' in v and v['propulsion_type'] == 'human' and v['form_factor'] == 'cargo_bicycle',
                GbfsStation.update_cargo,
                GbfsVehicle.update_cargo,
            ),

            (
                lambda v: 'propulsion_type' in v and v['propulsion_type'] == 'electric_assist' and v['form_factor'] == 'cargo_bicycle',
                GbfsStation.update_ecargo,
                GbfsVehicle.update_ecargo
            ),
            (
                lambda v: 'propulsion_type' in v and v['propulsion_type'] == 'electric' and 'scooter' in v['form_factor'],
                GbfsStation.update_scooter,
                GbfsVehicle.update_scooter,
            ),

        ]

    def get_feeds(self, url, scraper, force_https):
        if self.feeds:
            return self.feeds

        feed_data = scraper.request(url, params=self.req_args, raw=True)

        # do not hide Unauthorized or Too many requests status codes
        if scraper.last_request.status_code in [401, 429]:
            raise Exception(feed_data)

        if scraper.last_request.status_code >= 400:
            # GBFS service description not found. Try to guess based on
            # defaults
            return self.default_feeds

        feed_data = json.loads(feed_data)
        feeds = {}

        # Prefer "en", if not, take any
        lang = "en"

        if lang in feed_data['data']:
            feeds = feed_data['data'][lang]
        else:
            feeds = list(feed_data['data'].values()).pop()

        if isinstance(feeds, dict):
            feeds = feeds['feeds']

        for feed in feeds:
            if force_https:
                # Feed published with the wrong protocol
                feed['url'] = feed['url'].replace('http://', 'https://')

        return {feed['name']: feed['url'] for feed in feeds}


    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        if self.retry:
            scraper.retry = True
            scraper.retry_opts.update(self.retry)

        feeds = self.get_feeds(self.feed_url, scraper, self.force_https)

        # Station Information and Station Status data retrieval
        station_information = json.loads(
            scraper.request(feeds['station_information'], params=self.req_args)
        )['data']['stations']
        station_status = json.loads(
            scraper.request(feeds['station_status'], params=self.req_args)
        )['data']['stations']

        if 'vehicle_types' in feeds:
            vehicle_info = json.loads(scraper.request(feeds['vehicle_types'], params=self.req_args))
            vehicles = self.resolve_vehicles(vehicle_info)
        else:
            vehicles = {}

        if 'free_bike_status' in feeds:
            feral_bikes = json.loads(
                scraper.request(feeds['free_bike_status'], params=self.req_args)
            )['data']['bikes']
        else:
            feral_bikes = []

        # Filter station information by region_id if set
        if self.region_id:
            station_information = filter(
                lambda s: s.get('region_id') == self.region_id,
                station_information
            )

        # Aggregate status and information by uid
        # Note there's no guarantee that station_status has the same
        # station_ids as station_information.
        station_information = {s['station_id']: s for s in station_information}
        station_status = {s['station_id']: s for s in station_status}
        # Any station not in station_information will be ignored
        station_zip = (
            (station_information[uid], station_status[uid])
            for uid in station_information.keys()
        )

        # Filter station by bbox before parsing and appending to a list.
        # Some networks have a LOT of stations
        if self.bbox:
            def getter(zipinfo):
                info, status = zipinfo
                # some networks break spec by setting lat and lng in status
                lat = info.get('lat', status.get('lat'))
                lng = info.get('lon', status.get('lon'))
                return (lat, lng)

            station_zip = filter_bounds(station_zip, getter, self.bbox)

        stations = []

        for info, status in station_zip:
            # Some feeds have info keys set to none on status
            info.update({k: v for k, v in status.items() if v is not None})
            try:
                station = self.station_cls(info, vehicles)
            except exceptions.StationPlannedException:
                continue
            except Exception as e:
                if self.ignore_errors:
                    continue
                raise e

            stations.append(station)

        ##### Vehicles #####

        # XXX ignore vehicles that are in a station
        # are we interested in this information?
        feral_bikes = filter(lambda v: 'station_id' not in v, feral_bikes)

        if self.bbox:
            feral_bikes = filter_bounds(feral_bikes, lambda b: (b['lat'], b['lon']), self.bbox)

        # XXX Some feeds add vehicles regardless of station_id. These are probably
        # a station overflow. If we want to filter them out untoggle this, or
        # add them to the station count
        # latlngset = set([(s.latitude, s.longitude) for s in stations])
        # feral_bikes = filter(lambda v: (v['lat'], v['lon']) not in latlngset, feral_bikes)

        self.stations = stations
        self.vehicles = list(self.parse_vehicles(feral_bikes, vehicles))

    def parse_vehicles(self, vehicles, vehicles_info):
        for vehicle in vehicles:
            try:
                yield GbfsVehicle(vehicle, vehicles_info, self)
            except exceptions.UnhandledVehicleException as e:
                warn(e)

class GbfsStation(BikeShareStation):

    def __init__(self, info, vehicles_info):
        """
        Example info variable:
        {u'is_installed': 1, u'post_code': u'null', u'capacity': 31,
        u'name': u'Ft. York / Capreol Crt.', u'cross_street': u'null',
        u'num_bikes_disabled': 0, u'last_reported': 1473969337,
        u'lon': -79.395954, u'station_id': u'7000', u'is_renting': 1,
        u'num_docks_available': 26, u'num_docks_disabled': 0,
        u'address': u'Ft. York / Capreol Crt.', u'lat': 43.639832,
        u'num_bikes_available': 5, u'is_returning': 1}

        So let's extract the dataaa
        """
        super(GbfsStation, self).__init__()
        if not info['is_installed']:
            raise exceptions.StationPlannedException()

        self.name = get_text(info['name'])
        if 'num_bikes_available' in info:
            self.bikes = int(info['num_bikes_available'])
        elif 'num_vehicles_available' in info:
            self.bikes = int(info['num_vehicles_available']) # In GBFS 3.0, num_bikes_available is replaced by num_vehicles_available https://github.com/MobilityData/gbfs/blob/v3.0/gbfs.md#station_statusjson

        if 'num_docks_available' in info:
            self.free = int(info['num_docks_available'])

        self.latitude = float(info['lat'])
        self.longitude = float(info['lon'])
        self.extra = {
            'uid': info['station_id'],
            'renting': info['is_renting'],
            'returning': info['is_returning'],
        }

        if 'last_reported' in info:
            self.extra["last_updated"] = info['last_reported']

        if 'address' in info:
            self.extra['address'] = info['address']
        if 'post_code' in info:
            self.extra['post_code'] = info['post_code']

        if 'num_ebikes_available' in info:
            self.extra['has_ebikes'] = True
            self.extra['ebikes'] = int(info['num_ebikes_available'])

        if 'num_bikes_available_types' in info:
            bike_types = info['num_bikes_available_types']
            if 'ebike' in bike_types:
                self.extra['has_ebikes'] = True
                self.extra['ebikes'] = int(bike_types['ebike'])
                self.extra['normal_bikes'] = int(bike_types['mechanical'])

        if 'rental_methods' in info:
            payment = list(map(str.lower, info['rental_methods']))
            self.extra['payment'] = payment
            self.extra['payment-terminal'] = 'creditcard' in payment

        if 'altitude' in info:
            self.extra['altitude'] = info['altitude']

        if 'capacity' in info:
            self.extra['slots'] = info['capacity']

        if 'vehicle_types_available' in info:
            for vehicle in info['vehicle_types_available']:
                if vehicle['vehicle_type_id'] not in vehicles_info:
                    continue
                vi, resolve_s, _ = vehicles_info[vehicle['vehicle_type_id']]
                resolve_s(self, vehicle, vi)

            # dott feeds set num_bikes_available=0 but contain the information
            # on vehicle_types_available ...
            # XXX on a 2.3 and 3 parser we could only trust these
            if not self.bikes:
                self.bikes = sum([
                    self.extra.get('normal_bikes', 0),
                    self.extra.get('ebikes', 0),
                ])

        if 'rental_uris' in info and isinstance(info['rental_uris'], dict):
            self.extra['rental_uris'] = {}
            if 'android' in info['rental_uris']:
                self.extra['rental_uris']['android'] = info['rental_uris']['android']
            if 'ios' in info['rental_uris']:
                self.extra['rental_uris']['ios'] = info['rental_uris']['ios']
            if 'web' in info['rental_uris']:
                self.extra['rental_uris']['web'] = info['rental_uris']['web']

        self.extra['virtual'] = info.get('is_virtual_station', False)

    def update_normal_bikes(self, vehicle, info):
        self.extra.setdefault('normal_bikes', 0)
        self.extra['normal_bikes'] += vehicle['count']

    def update_ebikes(self, vehicle, info):
        self.extra.setdefault('ebikes', 0)
        self.extra['ebikes'] += vehicle['count']
        self.extra['has_ebikes'] = True

    def update_ecargo(self, vehicle, info):
        self.extra.setdefault('ecargo', 0)
        self.extra['ecargo'] += vehicle['count']
        self.extra['has_ecargo'] = True

    def update_cargo(self, vehicle, info):
        self.extra.setdefault('cargo', 0)
        self.extra['cargo'] += vehicle['count']
        self.extra['has_cargo'] = True

    def update_scooter(self, vehicle, info):
        self.extra.setdefault('scooters', 0)
        self.extra['scooters'] += vehicle['count']
        self.extra['has_scooters'] = True


Gbfs.station_cls = GbfsStation

class GbfsVehicle(Vehicle):
    def __init__(self, data, vehicle_types, system):
        extra = {
            "uid": data["bike_id"],
            "online": not data["is_disabled"],
        }
        super().__init__(data["lat"], data["lon"], extra=extra, system=system)
        if 'vehicle_type_id' in data:
            vi, _, r = vehicle_types[data['vehicle_type_id']]
            r(self, data, vi)
        else:
            self.kind = VehicleTypes.default

        if 'current_fuel_percent' in data:
            self.extra['battery'] = float(data['current_fuel_percent'])

        # undocumented field found in the wild, usually on GBFS 1.1 Lyft feeds
        # XXX move these feeds to GBFS 2.3
        if 'type' in data:
            if data['type'] == 'electric_bike':
                self.kind = VehicleTypes.ebike
            elif data['type'] == 'electric_scooter':
                self.kind = VehicleTypes.scooter
            else:
                warn("Unhandled vehicle type '%s'" % data['type'])

    def update_normal_bikes(self, vehicle, info):
        self.kind = VehicleTypes.bicycle

    def update_ebikes(self, vehicle, info):
        self.kind = VehicleTypes.ebike

    def update_ecargo(self, vehicle, info):
        self.kind = VehicleTypes.ebike

    def update_cargo(self, vehicle, info):
        self.kind = VehicleTypes.bicycle

    def update_scooter(self, vehicle, info):
        self.kind = VehicleTypes.scooter
