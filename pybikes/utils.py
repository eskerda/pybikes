# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import os
import re

import requests
from requests.adapters import HTTPAdapter, Retry
from shapely.geometry import Point, box, shape

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.compat import map


class PyBikesScraper(object):

    last_request = None

    def __init__(
        self,
        cachedict=None,
        headers=None,
        user_agent='PyBikes',
        retry=False,
        retry_opts=None,
        proxy_enabled=False,
        proxies=None,
        session=None,
        requests_timeout=300,
        ssl_verification=True,
        parse_cookies=True,
    ):
        self.headers = headers if isinstance(headers, dict) else {}
        self.headers.setdefault('User-Agent', user_agent)

        self.proxy_enabled = proxy_enabled
        self.proxies = proxies if isinstance(proxies, dict) else {}

        self.retry = retry
        self.retry_opts = retry_opts if isinstance(retry_opts, dict) else {}

        self.cachedict = cachedict

        self.session = session or requests.session()
        self.requests_timeout = requests_timeout
        self.ssl_verification = ssl_verification
        self.parse_cookies = parse_cookies

    def setUserAgent(self, user_agent):
        self.headers['User-Agent'] = user_agent

    def request(self, url, method='GET', params=None, data=None, raw=False,
                headers=None, default_encoding='UTF-8', skip_cache=False,
                ssl_verification=True):
        if self.retry:
            retries = Retry(** self.retry_opts)
            self.session.mount(url, HTTPAdapter(max_retries=retries))

        _headers = self.headers.copy()
        _headers.update(headers or {})

        # XXX proper encode arguments for proper call args -> response
        if self.cachedict and url in self.cachedict and not skip_cache:
            response = self.cachedict[url]
        else:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                proxies=self.getProxies(),
                headers=_headers,
                # some endpoints might fail verification, so it's up to the spider
                # to disable it
                verify=self.ssl_verification and ssl_verification,
                timeout=self.requests_timeout,
            )

        data = response.text

        # Somehow requests defaults to ISO-8859-1 (when no encoding
        # specified). Put it back to UTF-8 by default
        if 'charset' not in response.headers:
            if 'Content-Type' in response.headers:
                if 'text' in response.headers['Content-Type']:
                    response.encoding = default_encoding
                    data = response.text
        if raw:
            data = response.content

        if self.parse_cookies and 'set-cookie' in response.headers:
            self.headers['Cookie'] = response.headers['set-cookie']

        self.last_request = response

        if self.cachedict is not None:
            self.cachedict[url] = response

        return data

    def clearCookie(self):
        if 'Cookie' in self.headers:
            del self.headers['Cookie']

    def setProxies(self, proxies):
        self.proxies = proxies

    def getProxies(self):
        if self.proxy_enabled:
            return self.proxies
        else:
            return {}

    def enableProxy(self):
        self.proxy_enabled = True

    def disableProxy(self):
        self.proxy_enabled = False


def filter_bounds(things, key, *point_bounds):
    def default_getter(thing):
        if isinstance(thing, BikeShareStation):
            return (thing.latitude, thing.longitude)
        return (thing[0], thing[1])

    key = key or default_getter

    bounds = []
    for pb in point_bounds:
        # Assume that a 2 length bound list is a square NE/SW
        # passed as a list of two (lat, lng) pairs
        # What we are exposing, are lat, lng pairs. So we keep consistency
        # expecting (lat, lng) pairs, (y, x) instead of (x, y) pairs
        if isinstance(pb, list) and len(pb) == 2:
            bb = box(pb[1][1], pb[1][0], pb[0][1], pb[0][0])
        # bbox as [minX, minY, maxX, maxY]
        elif isinstance(pb, list) and len(pb) == 4:
            bb = box(* pb)
        # Support GeoJSON features
        elif isinstance(pb, dict):
            bb = shape(pb).buffer(0)
        else:
            raise TypeError("Point bounds only supports lists and dicts.")
        bounds.append(bb)

    for thing in things:
        # What we are exposing, are lat, lng pairs. So we keep consistency
        # expecting (lat, lng) pairs, (y, x) instead of (x, y) pairs
        point = Point(*reversed(key(thing)))
        if not any(map(lambda pol: pol.contains(point), bounds)):
            continue
        yield thing


class Bounded(object):
    """ Class mixin providing automatic bound filtering to stations """
    bounds = None
    _stations = None

    def __init__(self, * args, ** kwargs):
        self._stations = []
        self.bounds = kwargs.pop('bounds', None)
        super(Bounded, self).__init__(* args, ** kwargs)

    @property
    def stations(self):
        return self._stations

    @stations.setter
    def stations(self, value):
        # XXX: note that any list method applied to self.stations will
        # circumvent this method (such as append)
        if self.bounds:
            value = list(filter_bounds(value, None, self.bounds))
        self._stations = value


class Keys:
    def __getattr__(self, key):
        return os.environ.get('PYBIKES_%s' % key.upper())

keys = Keys()
keys.bicimad = {
    'passkey': keys.bicimad_passkey,
    'clientid': keys.bicimad_clientid,
}
keys.weelo = {
    'client_id': keys.weelo_client_id,
    'client_secret': keys.weelo_client_secret,
}
keys.deutschebahn = {
    'client_id': keys.deutschebahn_client_id,
    'client_secret': keys.deutschebahn_client_secret,
}
