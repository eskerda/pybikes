# -*- coding: utf-8 -*-
"""
Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import re
import urllib.request, urllib.error, urllib.parse
import html.entities

def str2bool(v):
  return v.lower() in ["yes", "true", "t", "1"]
  

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    r = ''.join(rc)
    if r == '':
        return None
    else:
        return r

def getTextTag(element, tag, index = 0):
    return getText(element.getElementsByTagName(tag)[index].childNodes)

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