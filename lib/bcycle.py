# -*- coding: utf-8 -*-

from station import Station
import re
import urllib,urllib2
from datetime import datetime
from BeautifulSoup import BeautifulSoup

""" We want this shit 
      var point = new google.maps.LatLng(41.86727, -87.61527);
      var marker = new createMarker(point, "<div class='location'><strong>Museum Campus</strong><br />1200 S Lakeshore Drive<br />Chicago, IL 60605</div><div class='avail'>Bikes available: <strong>0</strong><br />Docks available: <strong>21</strong></div><br/>", icon, back);
"""

LAT_LNG_RGX = "var\ point\ =\ new\ google.maps.LatLng\(([+-]?\\d*\\.\\d+)(?![-+0-9\\.])\,\ ([+-]?\\d*\\.\\d+)(?![-+0-9\\.])\)"
DATA_RGX = "var\ marker\ =\ new\ createMarker\(point\,(.*?)\,\ icon\,\ back\)"


class BCycleStation(Station):
  
  prefix = ""
  main_url = ""
    
  def update(self):
      return self
  
  def fromHtml(self,raw):
      soup = BeautifulSoup(raw)
      self.name = soup.contents[1].contents[0].renderContents()
      self.bikes = soup.contents[2].contents[1].renderContents()
      self.free = soup.contents[2].contents[4].renderContents()
      self.description = soup.contents[1].contents[2]+". "+soup.contents[1].contents[4]
      return self
  def to_json(self):
      text =  '{"id":"%s", "name":"%s", "lat":"%s", "lng":"%s", "timestamp":"%s", "bikes":%s, "free":%s, "description":"%s"}' % \
      (self.idx, self.name, self.lat, self.lng, self.timestamp, self.bikes, self.free, self.description)
      print text.encode('utf-8'),
      return text.encode('utf-8')
    

def get_all(spec):
  usock = urllib2.urlopen(spec.main_url)
  raw_data = usock.read()
  usock.close()
  geopoints = re.findall(LAT_LNG_RGX, raw_data)
  data = re.findall(DATA_RGX, raw_data)
  stations = []
  for index,d in enumerate(data):
    station = spec(index)
    station.lat = int(float(geopoints[index][0])*1E6)
    station.lng = int(float(geopoints[index][1])*1E6)
    station.fromHtml(d)
    stations.append(station)
  return stations
  
  