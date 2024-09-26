# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
from warnings import warn

from pybikes import BikeShareSystem, BikeShareStation, exceptions
from pybikes.utils import PyBikesScraper, filter_bounds
from pybikes.compat import urljoin, urlparse, parse_qs

try:
    # Python 2
    unicode
except NameError:
    # Python 3
    unicode = str


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
        ignore_errors=False,
        retry=None,
        bbox=None,
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

    @property
    def default_feeds(self):
        url = self.feed_url
        return {
            "station_information": urljoin(url, 'station_information.json'),
            "station_status": urljoin(url, 'station_status.json'),
        }

    @property
    def vehicle_taxonomy(self):
        def update_normal_bikes(station, vehicle, info):
            station.extra.setdefault('normal_bikes', 0)
            station.extra['normal_bikes'] += vehicle['count']

        def update_ebikes(station, vehicle, info):
            station.extra.setdefault('ebikes', 0)
            station.extra['ebikes'] += vehicle['count']
            station.extra['has_ebikes'] = True

        def update_ecargo(station, vehicle, info):
            station.extra.setdefault('ecargo', 0)
            station.extra['ecargo'] += vehicle['count']
            station.extra['has_ecargo'] = True

        def update_cargo(station, vehicle, info):
            station.extra.setdefault('cargo', 0)
            station.extra['cargo'] += vehicle['count']
            station.extra['has_cargo'] = True

        # contains pairs of (vehicle query, resolver)
        return [
            (
                lambda v: 'propulsion_type' in v and v['propulsion_type'] == 'human' and v['form_factor'] == 'bicycle',
                update_normal_bikes
            ),
            (
                lambda v: 'propulsion_type' in v and v['propulsion_type'] in ['electric_assist', 'electric'] and v['form_factor'] == 'bicycle',
                update_ebikes
            ),
            (
                lambda v: 'propulsion_type' in v and v['propulsion_type'] == 'human' and v['form_factor'] == 'cargo_bicycle',
                update_cargo
            ),

            (
                lambda v: 'propulsion_type' in v and v['propulsion_type'] == 'electric_assist' and v['form_factor'] == 'cargo_bicycle',
                update_ecargo
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
            # Useful for warning possible interesting types of vehicles that
            # we do not support
            def noop(s, v, i):
                warn("Unhandled vehicle type %s with count %d" % (i, v['count']))

            vehicle_info = json.loads(scraper.request(feeds['vehicle_types'], params=self.req_args))
            # map vehicle id to vehicle info AND extra info resolver
            # for direct access
            vehicles = {
                # TODO: ungrok this line
                v.get('vehicle_type_id', 'err'): (v, next(iter((r for q, r in self.vehicle_taxonomy if q(v))), noop))
                    for v in vehicle_info['data'].get('vehicle_types', [])
            }
        else:
            vehicles = {}

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

        self.stations = stations


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

        self.name = unicode(info['name'])
        self.bikes = int(info['num_bikes_available'])

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
            payment = list(map(unicode.lower, info['rental_methods']))
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
                vi, resolve = vehicles_info[vehicle['vehicle_type_id']]
                resolve(self, vehicle, vi)

        if 'rental_uris' in info and isinstance(info['rental_uris'], dict):
            self.extra['rental_uris'] = {}
            if 'android' in info['rental_uris']:
                self.extra['rental_uris']['android'] = info['rental_uris']['android']
            if 'ios' in info['rental_uris']:
                self.extra['rental_uris']['ios'] = info['rental_uris']['ios']
            if 'web' in info['rental_uris']:
                self.extra['rental_uris']['web'] = info['rental_uris']['web']



Gbfs.station_cls = GbfsStation
