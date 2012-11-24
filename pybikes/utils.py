# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import requests

def str2bool(v):
  return v.lower() in ["yes", "true", "t", "1"]

class PyBikesScrapper(object):
    
    headers = {
        'User-Agent': 'PyBikes'
    }

    proxies = {}

    proxy_enabled = False

    last_request = None

    def __init__(self):

        self.session = requests.session( headers = self.headers )


    def setUserAgent(self, user_agent):

        self.headers['User-Agent'] = user_agent

    def request(self, url, method = 'GET', params = None, data = None):

        response = self.session.request(
            method = method,
            url = url,
            params = params,
            data = data,
            proxies = self.getProxies(),
            headers = self.headers,
            verify = False
        )
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