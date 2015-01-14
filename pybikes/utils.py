# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import re
import urllib, urllib2
from urlparse import urlparse

import requests

def str2bool(v):
  return v.lower() in ["yes", "true", "t", "1"]

def url_scheme(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme

def sp_capwords(word):
    blacklist = [
        u'el', u'la', u'los', u'las', \
        u'un', u'una', u'unos', u'unas', \
        u'lo', u'al', u'del', \
        u'a', u'ante', u'bajo', u'cabe', u'con', u'contra', u'de', u'desde', \
        u'en', u'entre', u'hacia', u'hasta', u'mediante', u'para', u'por', \
        u'según', u'sin' \
        # Catala | Valencia | Mallorqui
        u'ses', u'sa', u'ses'
    ]
    word = word.lower()
    cap_lambda = lambda (index, w): \
                    w.capitalize() if index == 0 or w not in blacklist \
                                   else w
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

    def __init__(self, cachedict = None):
        self.headers = { 'User-Agent': 'PyBikes' }
        self.proxies = {}
        self.session = requests.session()
        self.cachedict = cachedict

    def setUserAgent(self, user_agent):
        self.headers['User-Agent'] = user_agent

    def __proxy_https_req__(self, url):
            proxy = urllib2.ProxyHandler(self.proxies)
            opener = urllib2.build_opener(proxy)
            response = opener.open(url)
            data = response.read()
            if "charset" in response.headers['content-type']:
                encoding = response.headers['content-type']\
                    .split('charset=')[-1]
                data = unicode(data, encoding)
            return (response, data)

    def request(self, url, method = 'GET', params = None, data = None):
        if self.cachedict and url in self.cachedict:
            return self.cachedict[url]
        if self.proxy_enabled and url_scheme(url) == 'https':
            response, data = self.__proxy_https_req__(url)
        else:
            response = self.session.request(
                method = method,
                url = url,
                params = params,
                data = data,
                proxies = self.getProxies(),
                headers = self.headers,
                verify = False
            )
            data = response.text
        if 'set-cookie' in response.headers:
            self.headers['Cookie'] = response.headers['set-cookie']
        self.last_request = response
        if self.cachedict is not None:
            self.cachedict[url] = data
        return data

    def clearCookie(self):
        if 'Cookie' in self.headers:
            del self.headers['Cookie']

    def setProxies(self, proxies ):
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

