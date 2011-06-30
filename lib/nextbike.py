# -*- coding: utf-8 -*-

from station import Station
import urllib,urllib2
from datetime import datetime
import re
from BeautifulSoup import BeautifulStoneSoup

URL = "http://www.nextbike.de/maps/nextbike-official.xml?domain=de"


def clean_string(string):
  string = re.sub(r'[^\w]', '', string)
  return string.lower().encode('utf-8')
  
  
class NextBikeStation(Station):
  def __init__(self, idx, pfx):
    Station.__init__(self,idx)
    self.prefix = clean_string(pfx)
  
  def from_xml(self, data):
    self.name = data.get("name")
    self.uid = data.get("uid")
    self.bikes = int(clean_string(data.get("bikes")))
    self.free = data.get("racks")
    if self.free is None:
      self.free = -1
    
    self.number = data.get("number")
    self.bike_numbers = data.get("bike_numbers")
    self.spot = int(data.get("spot"))
    self.lat = int(float(data.get("lat"))*1E6)
    self.lng = int(float(data.get("lng"))*1E6)
    return self
  
  def to_json(self):
    text =  '{id:"%s", uid:"%s", name:"%s", lat:"%s", lng:"%s", timestamp:"%s", spot:%s, bikes:%s' % \
    (self.idx, self.uid, self.name, self.lat, self.lng, self.timestamp, self.spot, self.bikes)
    if self.free is not None:
      text = text+', free:%s' % self.free
    if self.number is not None:
      text = text+', number:%s' % self.number
    if self.bike_numbers is not None:
      text = text+', bike_numbers:"%s"' % self.bike_numbers
    text = text+'}'
    return unicode(text)
  
def get_all():
  raw_data = get_data()
  soup = BeautifulStoneSoup(raw_data)
  cities = soup.findAll("city")
  stations = []
  for city in cities:
    name = city.get("name")
    l_stations = city.findAll("place")
    for index, station in enumerate(l_stations):
      sta = NextBikeStation(index,name)
      sta.from_xml(station)
      stations.append(sta)
  return stations
  
def get_data():
  request = urllib2.Request(URL)
  opener = urllib2.build_opener()
  request.add_header('User-Agent','Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.375.99 Safari/533.4')
  raw_data = opener.open(request).read()
  return raw_data
  
def get_services():
  raw_data = get_data()
  soup = BeautifulStoneSoup(raw_data)
  cities = soup.findAll("city")
  services = []
  for city in cities:
    services.append(clean_string(city.get("name")))
  return services
  
  
  
	
	
	
	