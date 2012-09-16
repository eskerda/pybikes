# -*- coding: utf-8 -*-
from station import Station

import urllib,urllib2
from BeautifulSoup import BeautifulStoneSoup
import re
from datetime import datetime

ACTION_URL = "/public/mobapp/maq.asmx/{0}"
STATION_LIST = "getRacks"
STATION_INFO = "getRack"

    
def get_all(spec, prefix=""):
  url = "%s%s" % (spec.url, ACTION_URL.format(STATION_LIST))
  usock = urllib2.urlopen(prefix+url)
  xml_data = usock.read()
  usock.close()
  soup = BeautifulStoneSoup(xml_data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
  data = BeautifulStoneSoup(soup.find('string').contents[0])
  markers = data.findAll('station')
  stations = []
  idx = 0
  for marker in markers:
    try:
      number = int(marker.contents[0])
      if (number < 500):
        station = spec(idx, number)
        stations.append(station)
        idx = idx + 1
    except Exception:
      pass
  return stations
  
class SmartBikeCCStation(Station):
  prefix = ""
  url = ""

  def __init__(self, idx, internal_id):
    Station.__init__(self, idx)
    self.number = internal_id
    """
     Takes too long to instantiate all the stations, but the
     smartbike API does not give any useful information for
     starters.. :(
    """
    self.update()
  
  def update(self, prefix = ""):
    usock = urllib2.urlopen(prefix+"%s%s" % (self.url, ACTION_URL.format(STATION_INFO)), urllib.urlencode({'id': self.number}))
    xml_data = usock.read()
    usock.close()
    soup = BeautifulStoneSoup(xml_data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
    self.from_xml(soup)
    self.timestamp = datetime.now()
    return self
    
  def from_xml(self, xml_data):
    
    """ xml marker object as in
    <string xmlns="http://smartbikeportal.clearchannel.no/public/mobapp/">
      <station>
        <ready_bikes>5</ready_bikes>
        <empty_locks>13</empty_locks>
        <online>1</online>
        <description>01-Middelthunsgate (vis-a-vis nr. 21, retning Kirkeveien)</description>
        <longitute>10.709009170532226</longitute>
        <latitude>59.92786125852981</latitude>
      </station>
    </string>
    """
    data = BeautifulStoneSoup(xml_data.find('string').contents[0])
    data = data.contents[0]
    self.bikes = int(data.find('ready_bikes').contents[0])
    self.free = int(data.find('empty_locks').contents[0])
    self.name = str(data.find('description').contents[0])
    self.lat = int(float(data.find('latitude').contents[0])*1E6)
    self.lng = int(float(data.find('longitute').contents[0])*1E6)
    return self
