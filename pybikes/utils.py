# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import requests


def str2bool(v):
    return v.lower() in ["yes", "true", "t", "1"]


def sp_capwords(word):
    blacklist = [
        u'el', u'la', u'los', u'las',
        u'un', u'una', u'unos', u'unas',
        u'lo', u'al', u'del',
        u'a', u'ante', u'bajo', u'cabe', u'con', u'contra', u'de', u'desde',
        u'en', u'entre', u'hacia', u'hasta', u'mediante', u'para', u'por',
        u'según', u'sin',
        # Catala | Valencia | Mallorqui
        u'ses', u'sa', u'ses'
    ]
    word = word.lower()
    cap_lambda = lambda (i, w): w.capitalize() if i == 0 or w not in blacklist else w
    return " ".join(map(cap_lambda, enumerate(word.split())))


def clean_string(dirty):
    # Way generic strip_tags. This is unsafe in some cases, but gets the job
    # done for most inputs
    dirty = re.sub(r'<[^>]*?>', '', dirty)
    # Decode any escaped sequences
    dirty = dirty.encode('utf-8').decode('unicode_escape')
    return dirty


class PyBikesScraper(object):
    proxy_enabled = False
    last_request = None
    ssl_verification = True

    def __init__(self, cachedict=None):
        self.headers = {'User-Agent': 'PyBikes'}
        self.proxies = {}
        self.session = requests.session()
        self.cachedict = cachedict

    def setUserAgent(self, user_agent):
        self.headers['User-Agent'] = user_agent

    def request(self, url, method='GET', params=None, data=None, raw=False,
                default_encoding='UTF-8'):
        if self.cachedict and url in self.cachedict:
            return self.cachedict[url]
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            proxies=self.getProxies(),
            headers=self.headers,
            # some endpoints might fail verification, so it's up to the spider
            # to disable it
            verify=self.ssl_verification,
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

        if 'set-cookie' in response.headers:
            self.headers['Cookie'] = response.headers['set-cookie']
        self.last_request = response
        if self.cachedict is not None:
            self.cachedict[url] = data
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
