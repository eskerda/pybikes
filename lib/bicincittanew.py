# -*- coding: utf-8 -*-
from station import Station

import re
import urllib,urllib2

RE_INFO="RefreshMap\((.*?)\)"

def get_all(spec, start_range = 0):
    usock = urllib2.urlopen(spec.main_url)
    data = usock.read()
    usock.close()
    data = unicode(data.decode('iso8859-15'))
	
    raw = re.findall(RE_INFO, data)
    info = raw[1].split('\',\'')
    for idx,inf in enumerate(info):
      info[idx] = inf.split('|')
    stations = []

    for idx in range(len(info[0])):
        station = spec(idx+start_range)
        name = re.sub('\:*$','',info[5][idx])
        description = info[7][idx]
        lat = int(float(info[3][idx])*1E6)
        lng = int(float(info[4][idx])*1E6)
        bikes = info[6][idx].count('4')
        free = info[6][idx].count('0')
        station.fromData(name, description, lat, lng, bikes, free)
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

