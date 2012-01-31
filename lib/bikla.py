# -*- coding: utf-8 -*-
from station import Station

import urllib,urllib2
from datetime import datetime
from BeautifulSoup import BeautifulSoup

PREFIX = "bikla"
URL = "http://www.bikla.net/loadBiklaDB.php?esta=1"
ROOT = "http://www.bikla.net"
OBJECT_SEP = "8Z-kT"
FIELD_SEP = "tK-z8"
STATUS = 5
CICLOPUERTO = 4
HTML = 3
LAT = 1
LNG = 2
IDX = 0

def get_all():
  
  opener = urllib2.build_opener()
  opener.addheaders = [('User-Agent', 'CityBikes API')]
  data = opener.open(URL).read()
  # A fuzzle is a puzzle full of fuck
  fuzzles = data.split(OBJECT_SEP)
  stations = []
  for index, fuzzle in enumerate(fuzzles):
    station = BiklaStation(index)
    station.from_fuzzle(fuzzle)
    stations.append(station)
  return stations
  
class BiklaStation(Station):
  prefix = PREFIX
  main_url = URL
  
  def update(self):
    return self
    
  def from_fuzzle(self, fuzzle):
    fields = fuzzle.split(FIELD_SEP)
    self.number = fields[IDX]
    self.lat = int(float(fields[LAT])*1E6)
    self.lng = int(float(fields[LNG])*1E6)
    
    soup = BeautifulSoup(fields[HTML])
    divs = soup.findAll('div')
    
    self.media = "%s%s" % (ROOT, soup.img['src'])
    self.name = divs[1].contents[0].string
    self.bikes = int(divs[3].contents[0].split(':')[1])
    self.free = int(divs[3].contents[2].split(':')[1])
    self.status = fields[STATUS]
    self.meta = ""
    for c in divs[2].contents:
      if (str(c) != "<br />"):
	self.meta = "%s,%s" % (self.meta, str(c))
    self.meta = self.meta[1:]
    return self