# -*- coding: utf-8 -*-
from station import Station

import urllib,urllib2
from datetime import datetime
from xml.dom import minidom


PREFIX = "decobike"
URL = "http://decobike.com/playmoves.xml"


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
    
    

def get_all():
  usock = urllib2.urlopen(URL)
  xml_data = usock.read()
  usock.close()
  dom = minidom.parseString(xml_data)
  markers = dom.getElementsByTagName('location')
  stations = []
  for index, marker in enumerate(markers):
    station = DecobikeStation(index)
    station.from_xml(marker)
    stations.append(station)
  return stations
  
  
class DecobikeStation(Station):
  prefix = PREFIX
  main_url = URL

  def to_json(self):
    text =  '{id:"%s", name:"%s", lat:"%s", lng:"%s", timestamp:"%s", bikes:%s, free:%s, number:"%s"}' % \
    (self.idx, self.name, self.lat, self.lng, self.timestamp, self.bikes, self.free, self.number)
    print text.encode('utf-8'),
    return text.encode('utf-8')
  
  def update(self):
    return self
    
  def from_xml(self, xml_data):
    
    """ xml marker object as in
      <location>
	  <Id>201</Id>
	  <Address>19th Street &amp; Dade Blvd</Address>
	  <Distance>0.67</Distance>
	  <Latitude>25.7948074</Latitude>
	  <Longitude>-80.13935</Longitude>
	  <Bikes>0</Bikes>
	  <Dockings>1</Dockings>
	  <StationAdList></StationAdList>
	</location>
    """
    
    self.number = int(getText(xml_data.getElementsByTagName("Id")[0].childNodes))
    self.name = unicode(getText(xml_data.getElementsByTagName("Address")[0].childNodes))
    self.lat = int(float(getText(xml_data.getElementsByTagName("Latitude")[0].childNodes))*1E6)
    self.lng = int(float(getText(xml_data.getElementsByTagName("Longitude")[0].childNodes))*1E6)
    self.bikes = int(getText(xml_data.getElementsByTagName("Bikes")[0].childNodes))
    self.free = int(getText(xml_data.getElementsByTagName("Dockings")[0].childNodes))
    return self