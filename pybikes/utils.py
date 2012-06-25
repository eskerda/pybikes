import re
import urllib2
import htmlentitydefs

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
        
        self.proxy_handler = urllib2.BaseHandler
        self.opener = None

    def setUserAgent(self, user_agent):

        self.headers['User-Agent'] = user_agent

    def request(self, url):
        
        if self.opener is None:
            self.opener = urllib2.build_opener(self.proxy_handler)

        req = urllib2.Request(url, headers = self.headers)
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
            self.opener = urllib2.build_opener(proxy_handler)