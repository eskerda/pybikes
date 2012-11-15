# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import urllib.request, urllib.error, urllib.parse

def str2bool(v):
  return v.lower() in ["yes", "true", "t", "1"]

class PyBikesScrapper(object):
    
    headers = {
        'User-Agent': 'PyBikes'
    }

    def __init__(self):
        
        self.proxy_handler = urllib.request.BaseHandler
        self.opener = None

    def setUserAgent(self, user_agent):

        self.headers['User-Agent'] = user_agent

    def request(self, url):
        
        if self.opener is None:
            self.opener = urllib.request.build_opener(self.proxy_handler)

        req = urllib.request.Request(url, headers = self.headers)
        response = self.opener.open(req)
        headers = response.info()
        if 'set-cookie' in headers:
            self.headers['Cookie'] = headers['set-cookie']
        
        return response

    def clearCookie(self):
        
        if 'Cookie' in self.headers:
            del self.headers['Cookie']

    def setProxy( proxy_handler ):

        self.proxy_handler = proxy_handler
        if self.opener is not None:
            self.opener = urllib.request.build_opener(proxy_handler)