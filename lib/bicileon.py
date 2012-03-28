# -*- coding: utf-8 -*-
from station import Station

import urllib,urllib2
from datetime import datetime
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup
import re


PREFIX = "bicileon"
PLACEMARK_URL = "http://maps.google.com/maps/ms?authuser=0&vps=2&ie=UTF8&msa=0&output=kml&msid=217954070276990723173.0004b7f93dd828947e1ff"
STAT_URL = "http://bicileon.com/estado/EstadoActual.asp"
RE_STATUS = "ESTADO\ \-\ \((.?)\/(.?)\)"

#ESTADO - (1/10)

def getStats(shit):
  re1='.*?'	# Non-greedy match on filler
  re2='(\\d+)'	# Integer Number 1
  re3='.*?'	# Non-greedy match on filler
  re4='(\\d+)'	# Integer Number 2

  rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
  m = rg.search(shit)
  if m:
      int1=m.group(1)
      int2=m.group(2)
      return [int(int1),int(int2)]
  else:
      return None
      
def get_all():
  usock = urllib2.urlopen(PLACEMARK_URL)
  xml_data = usock.read()
  usock.close()
  usock = urllib2.urlopen(STAT_URL)
  stat_data = usock.read()
  usock.close()
  dom = BeautifulStoneSoup(xml_data)
  markers = dom.findAll('placemark')
  statSoup = BeautifulSoup(stat_data)
  statData = []
  for idx,table in enumerate(statSoup.findAll('table',{'cellpadding':5, 'width':100})):
    names = table.findAll('td', {'class': 'titulo'})
    fuck = table.findAll('td', {'class':'lat2'})
    if (len(fuck) > 0):
      fuck = fuck[1].contents[0]
    else:
      fuck = statSoup.findAll('td', {'class': 'lat2'})[(idx*2)+1].contents[0]
    fuck = getStats(fuck)
    if fuck is not None:
      statData.append({
	'name':names[0].contents[0], 
	'bikes': fuck[0],
	'free': fuck[1]-fuck[0]})
  
  stations = []
  idx = 0
  for marker in markers:
      station = BicileonStation(idx)
      station.setName(marker.contents[1])
      station.setLatLng(marker.coordinates.contents[0].split(','))
      fuck = BeautifulSoup(marker.description.contents[0])
      station.setAvailability(fuck.contents[0].string, statData)
      stations.append(station)
      idx = idx+1
  return stations
  
  
class BicileonStation(Station):
  prefix = PREFIX
  
  def setName(self, name):
    self.name = unicode(name.contents[0])
    return self
  def setLatLng(self, LatLng):
    self.lat = int(float(LatLng[0])*1E6)
    self.lng = int(float(LatLng[1])*1E6)
    return self
  def setAvailability(self, desc, statData):
    found = False
    for s in statData:
      if len(desc) > 1 and desc in s.get('name'):
	self.bikes = s.get('bikes')
	self.free = s.get('free')
	found = True
	break;
    if not found:
      self.bikes = -1
      self.free = -1
    return self