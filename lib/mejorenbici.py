# -*- coding: utf-8 -*-
from station import Station

import urllib,urllib2
from datetime import datetime
from xml.dom import minidom


PREFIX = "mejorenbici"
URL = "http://www.insomniabs.net/maps3/CicloviasSense.kml"


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
  markers = dom.getElementsByTagName('Placemark')
  stations = []
  index = 0
  for idx,marker in enumerate(markers):
    station = MejorEnBiciStation(index)
    if station.from_xml(marker):
      stations.append(station)
      index = index+1
  return stations
  
  
class MejorEnBiciStation(Station):
  prefix = PREFIX
  main_url = URL
  
  def update(self):
    return self
    
  def from_xml(self, xml_data):
    
    """ 
    <Placemark>
    <name>Estacion Plaza Hussay</name>
    <description></description><styleUrl>#style17</styleUrl>
    <Point><coordinates>-58.398170,-34.599091,0.000000</coordinates></Point>
    </Placemark>
    Ignore anything without Point and coordinates (there are paths)
    """
    
    self.name = getText(xml_data.getElementsByTagName("name")[0].childNodes)
    self.description = getText(xml_data.getElementsByTagName("description")[0].childNodes)
    coords = getText(xml_data.getElementsByTagName("coordinates")[0].childNodes).split(',')
    if len(coords) == 3:
      self.lat = int(float(coords[1])*1E6)
      self.lng = int(float(coords[0])*1E6)
      self.bikes = -1
      self.free = -1
      return True
    else:
      return False