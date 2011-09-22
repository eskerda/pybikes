# -*- coding: utf-8 -*-
from station import Station

import urllib,urllib2
from datetime import datetime
from xml.dom import minidom


PREFIX = "ambiciat"
URL = "http://ambiciat.granollers.cat/ambiciat/estaciones/estacionesXML.aspx?dis=false&lib=false"


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
  markers = dom.getElementsByTagName('marker')
  stations = []
  for index, marker in enumerate(markers):
    station = AmbiciatStation(index)
    station.from_xml(marker)
    stations.append(station)
  return stations
  
  
class AmbiciatStation(Station):
  prefix = PREFIX
  main_url = URL
  
  def update(self):
    return self
    
  def from_xml(self, xml_data):
    
    """ xml marker object as in
	<marker nombre="Plaça Can Trullas" 
	latitud="41.60747689747505"
	longitud="2.2854244709014892" 
	libres="6" ocupadas="1"/>
    """
    self.name = unicode(xml_data.getAttribute("nombre"))
    try:
      self.lat = int(float(xml_data.getAttribute("latitud"))*1E6)
    except Exception:
      self.lat = int(float(xml_data.getAttribute("latitud").replace(",",""))*1E6)
    self.lng = int(float(str(xml_data.getAttribute("longitud")))*1E6)
    self.bikes = int(xml_data.getAttribute("libres"))
    self.free = int(xml_data.getAttribute("ocupadas"))