# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import requests
import urllib, urllib2
from urlparse import urlparse

def str2bool(v):
  return v.lower() in ["yes", "true", "t", "1"]

def url_scheme(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme

class PyBikesScraper(object):
    
    headers = {
        'User-Agent': 'PyBikes'
    }

    proxies = {}

    proxy_enabled = False

    last_request = None

    def __init__(self):

        self.session = requests.session()


    def setUserAgent(self, user_agent):

        self.headers['User-Agent'] = user_agent

    def request(self, url, method = 'GET', params = None, data = None):

        if self.proxy_enabled and url_scheme(url) == 'https':
            proxy = urllib2.ProxyHandler(self.proxies)
            opener = urllib2.build_opener(proxy)
            response = opener.open(url)
            data = response.read()
            if "charset" in response.headers['content-type']:
                encoding = response.headers['content-type'].split('charset=')[-1]
                data = unicode(data, encoding)
            self.last_request = response
            return data

        response = self.session.request(
            method = method,
            url = url,
            params = params,
            data = data,
            proxies = self.getProxies(),
            headers = self.headers,
            verify = False
        )
        if 'set-cookie' in response.headers:
            self.headers['Cookie'] = response.headers['set-cookie']
            
        self.last_request = response
        return response.text

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
