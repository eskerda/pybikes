# -*- coding: utf-8 -*-
from station import Station

import re
import urllib,urllib2

RE_INFO="RefreshMap\((.*?)\)"

def get_all(spec, start_range = 0):
    usock = urllib2.urlopen(spec.main_url)
    data = usock.read()
    usock.close()
	
    raw = re.findall(RE_INFO, data)
    raw[1] = raw[1].replace('\\\'', '´')
    info = re.findall("\'(.*?)\'",raw[1])
    for idx,inf in enumerate(info):
      info[idx] = inf.split('|')
    stations = []

    for idx in range(len(info[0])):
        station = spec(idx+start_range)
        station.fromData(info[5][idx],info[7][idx],int(float(info[3][idx])*1E6),int(float(info[4][idx])*1E6),int(info[6][idx].count("4")),int(info[6][idx].count("0")))
        stations.append(station)
    return stations

class BicincittaNewStation(Station):
  prefix = ""
  main_url = ""

  def fromData(self, name, description, lat, lng, bikes, free):
      self.name = name
      self.description = description
      self.lat = lat
      self.lng = lng
      self.bikes = bikes
      self.free = free
      return self

  def update(self):
    return self

  def to_json(self):
    text =  '{"id":"%s", "name":"%s", "lat":"%s", "lng":"%s", "timestamp":"%s", "bikes":%s, "free":%s, "description":"%s"}' % \
    (self.idx, self.name, self.lat, self.lng, self.timestamp, self.bikes, self.free, self.description)
    return unicode(text.decode('iso-8859-15'))
