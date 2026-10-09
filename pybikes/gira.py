# -*- coding: utf-8 -*-
# Copyright (C) 2010-2023, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
from datetime import datetime, timedelta, timezone

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper
from pybikes.compat import utcnow


class GiraSystem(BikeShareSystem):
    meta = {
        'system': 'Gira',
        'company': ['EMEL']
    }

    # A station whose data has not been refreshed for this long is offline
    stale_after = timedelta(hours=24)

    def __init__(self, tag, feed_url, meta):
        super( GiraSystem, self).__init__(tag, meta)
        self.feed_url = feed_url

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        data = json.loads(scraper.request(self.feed_url))
        stations = list(map(GiraStation, data['features']))

        # EMEL's feed can report estado = 'repair' for every station, even
        # while they are renting (seen on all 199 stations in October 2026).
        # Only trust 'estado' when at least one station reports 'active'.
        trust_status = any(s.extra['status'] == 'active' for s in stations)
        now = utcnow()
        for station in stations:
            fresh = (station.updated is None
                     or now - station.updated <= self.stale_after)
            active = station.extra['status'] == 'active' or not trust_status
            station.extra['online'] = fresh and active

        self.stations = stations


class GiraStation(BikeShareStation):
    def __init__(self, info):
        super(GiraStation, self).__init__()

        self.latitude = float(info['geometry']['coordinates'][0][1])
        self.longitude = float(info['geometry']['coordinates'][0][0])
        self.name = info['properties']['desig_comercial']
        self.bikes = int(info['properties']['num_bicicletas'])
        self.free = int(info['properties']['num_docas']) - self.bikes
        self.updated = parse_date(info['properties'].get('update_date'))
        self.extra = {
            'uid': info['properties']['id_expl'],
            'slots': info['properties']['num_docas'],
            'status': info['properties']['estado'],
            'online': info['properties']['estado'] == 'active',
        }
        if self.updated:
            self.extra['last_updated'] = self.updated.isoformat()


def parse_date(value):
    """ Parse EMEL's ISO 8601 'update_date' (e.g. 2026-10-09T22:15:01Z) as an
    aware UTC datetime. Returns None when missing or malformed """
    if not value:
        return None
    try:
        # datetime.fromisoformat only accepts a trailing 'Z' on python >= 3.11
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
