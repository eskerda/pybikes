# -*- coding: utf-8 -*-

from station import Station

import re
import urllib,urllib2

RE_GIF="TemporaryFiles/(.*?)'"
RE_INFO="RefreshMap\((.*?)\)"
PREFIX = "tobike"
URL = "http://www.tobike.it/frmLeStazioni.aspx"
URL_INFO = "http://comunicareImages.tobike.it/TemporaryFiles/"

def get_all():
    
    usock = urllib2.urlopen(URL)
    data = usock.read()
    usock.close()
    gif = re.findall(RE_GIF, data)

    usock = urllib2.urlopen(URL_INFO+gif[0])
    data = usock.read()
    usock.close()
	
    raw = re.findall(RE_INFO, data)
    info = re.findall("\'(.*?)\'",raw[0])
    for idx,inf in enumerate(info):
      info[idx] = inf.split('|')
    info.remove(info[9])

    stations = []

    for idx in range(len(info[0])):
        station = TOBikeStation(idx)
        station.fromData(info[5][idx],info[7][idx],int(float(info[3][idx])*1E6),int(float(info[4][idx])*1E6),int(info[6][idx].count("4")),int(info[6][idx].count("0")))
        stations.append(station)
    return stations

class TOBikeStation(Station):
  prefix = PREFIX
  main_url = URL

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
