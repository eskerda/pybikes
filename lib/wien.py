# -*- coding: utf-8 -*-
from station import Station

import urllib,urllib2
from datetime import datetime
from xml.dom import minidom


PREFIX = "wien"
URL = "http://dynamisch.citybikewien.at/citybike_xml.php"


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
    station = WienStation(index)
    station.from_xml(marker)
    stations.append(station)
  return stations
  
  
class WienStation(Station):
  prefix = PREFIX
  main_url = URL

  def to_json(self):
    text =  '{id:"%s", name:"%s", lat:"%s", lng:"%s", timestamp:"%s", bikes:%s, free:%s, number:"%s", internal_id:"%s", status:"%s", description:"%s", boxes:"%s"}' % \
    (self.idx, self.name, self.lat, self.lng, self.timestamp, self.bikes, self.free, self.number, self.internal_id, self.status, self.description, self.boxes)
    print text.encode('utf-8'),
    return text.encode('utf-8')
  
  def update(self):
    return self
    
  def from_xml(self, xml_data):
    
    """ xml marker object as in
	<station>
	<id>2001</id>
	<internal_id>1046</internal_id>
	<name>Wallensteinplatz</name>
	<boxes>18</boxes>
	<free_boxes>1</free_boxes>
	<free_bikes>17</free_bikes>
	<status>aktiv</status>
	<description></description>
	<latitude>48.229912</latitude>
	<longitude>16.371582</longitude>
	</station>
    """
    
    self.number = int(getText(xml_data.getElementsByTagName("id")[0].childNodes))
    self.name = unicode(getText(xml_data.getElementsByTagName("name")[0].childNodes))
    self.lat = int(float(getText(xml_data.getElementsByTagName("latitude")[0].childNodes))*1E6)
    self.lng = int(float(getText(xml_data.getElementsByTagName("longitude")[0].childNodes))*1E6)
    self.internal_id = int(getText(xml_data.getElementsByTagName("internal_id")[0].childNodes))
    self.bikes = int(getText(xml_data.getElementsByTagName("free_bikes")[0].childNodes))
    self.free = int(getText(xml_data.getElementsByTagName("free_boxes")[0].childNodes))
    self.status = unicode(getText(xml_data.getElementsByTagName("status")[0].childNodes))
    self.description = unicode(getText(xml_data.getElementsByTagName("description")[0].childNodes))
    self.boxes = int(getText(xml_data.getElementsByTagName("boxes")[0].childNodes))