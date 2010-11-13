# -*- coding: utf-8 -*-
from station import Station

import urllib,urllib2
from datetime import datetime
from xml.dom import minidom


PREFIX = "bixi"
URL = "https://profil.bixi.ca/data/bikeStations.xml"



def str2bool(v):
  return v.lower() in ["yes", "true", "t", "1"]
  

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
  markers = dom.getElementsByTagName('station')
  stations = []
  for index, marker in enumerate(markers):
    station = BixiStation(index)
    station.from_xml(marker)
    stations.append(station)
  return stations
  
  
class BixiStation(Station):
  prefix = PREFIX
  main_url = URL

  def to_json(self):
    text =  '{"id":"%s", "name":"%s", "lat":"%s", "lng":"%s", "timestamp":"%s", "bikes":%s, "free":%s, "number":"%s", "internal_id":"%s", "locked":"%s", "temporary":"%s", "installed":"%s" }' % \
    (self.idx, self.name, self.lat, self.lng, self.timestamp, self.bikes, self.free, self.number, self.internal_id, self.locked, self.temporary, self.installed)
    print text.encode('utf-8'),
    return text.encode('utf-8')
  
  def update(self):
    return self
    
  def from_xml(self, xml_data):
    
    """ xml marker object as in
	    <station>
		<id>1</id>
		<name>Notre Dame / Place Jacques Cartier</name>
		<terminalName>6001</terminalName>
		<lat>45.508183</lat>
		<long>-73.554094</long>
		<installed>true</installed>
		<locked>false</locked>
		<installDate>1276012920000</installDate>
		<removalDate />
		<temporary>false</temporary>
		<nbBikes>14</nbBikes>
		<nbEmptyDocks>17</nbEmptyDocks>
	    </station>
    """

    self.internal_id = int(getText(xml_data.getElementsByTagName("id")[0].childNodes))
    self.number = int(getText(xml_data.getElementsByTagName("terminalName")[0].childNodes))
    self.name = '%s - %s' % (unicode(getText(xml_data.getElementsByTagName("terminalName")[0].childNodes)), unicode(getText(xml_data.getElementsByTagName("name")[0].childNodes)))
    self.lat = int(float(getText(xml_data.getElementsByTagName("lat")[0].childNodes))*1E6)
    self.lng = int(float(getText(xml_data.getElementsByTagName("long")[0].childNodes))*1E6)
    self.bikes = int(getText(xml_data.getElementsByTagName("nbBikes")[0].childNodes))
    self.free = int(getText(xml_data.getElementsByTagName("nbEmptyDocks")[0].childNodes))
    self.locked = str2bool(getText(xml_data.getElementsByTagName("locked")[0].childNodes))
    self.installed = str2bool(getText(xml_data.getElementsByTagName("installed")[0].childNodes))
    self.temporary = str2bool(getText(xml_data.getElementsByTagName("temporary")[0].childNodes))