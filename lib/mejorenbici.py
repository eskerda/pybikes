# -*- coding: utf-8 -*-
from station import Station

import urllib,urllib2
from datetime import datetime
import re
from BeautifulSoup import BeautifulSoup

RE_LATLNG = "new\ GMarker\(new\ GLatLng\((.*?)\,(.*?)\)"

"""
openInfoWindowHtml('<div style="height:100px;"><span class="style1">RETIRO</span><br><span class="style2">Cant. Bicicletas disponibles: 33</span><br></div>',{maxWidth:10}); });
"""
RE_HTMLCONTENT = "openInfoWindowHtml\((.*?)\,[^\)]+\)"
PREFIX = "mejorenbici"
URL = "http://www.bicicletapublica.com.ar/mapa.aspx"


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
    
def getBikes(raw):
  re1='.*?'	# Non-greedy match on filler
  re2='(\\d+)'	# Integer Number 1

  rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
  m = rg.search(raw)
  if m:
    int1=m.group(1)
    return int1
  else:
    return -1

def get_all():
  usock = urllib2.urlopen(URL)
  html_data = usock.read()
  usock.close()
  latlngs = re.findall(RE_LATLNG, html_data)
  content = re.findall(RE_HTMLCONTENT, html_data)
  stations = []
  for idx, ll in enumerate(latlngs):
    station = MejorEnBiciStation(idx)
    station.from_mdata(ll, content[idx])
    stations.append(station)
  return stations
  
class MejorEnBiciStation(Station):
  prefix = PREFIX
  main_url = URL
  
  def update(self):
    return self
    
  def from_mdata(self, latlng, htmlcontent):
    self.lat = int(float(latlng[0])*1E6)
    self.lng = int(float(latlng[1])*1E6)
    raw = BeautifulSoup(htmlcontent)
    self.name = raw.contents[1].contents[0].string
    rawBikes = raw.contents[1].contents[2].string
    self.bikes = getBikes(rawBikes)
    self.free = -1
    return self