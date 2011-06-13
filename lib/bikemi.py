# -*- coding: utf-8 -*-
from station import Station

import re
import urllib,urllib2
from datetime import datetime
from xml.dom import minidom

PREFIX = "bikemi"
URL = "http://www.bikemi.com/localizaciones/localizaciones.php"

# How to scrape the data
XML_RE = re.compile(r"exml.parseString\('(.*)'\);")


def get_all( opener = urllib2.build_opener()):
  usock = opener.open(URL)
  data = usock.read()
  usock.close()
  xml = XML_RE.search(data).groups()[0]
  dom = minidom.parseString(xml.decode('iso-8859-15').encode('utf-8'))
  placemarks = dom.getElementsByTagName('Placemark')
  stations = []
  for index, placemark in enumerate(placemarks):
        station = BikemiStation(index)
        station.from_xml(placemark)
        station.timestamp = datetime.now()
        stations.append(station)
  return stations

class BikemiStation(Station):
  prefix = PREFIX
  main_url = URL

  def to_json(self):
    text =  '{id:"%s", name:"%s", coordinates: "%s", x:"%s", y:"%s", lat:"%s", lng:"%s", timestamp:"%s", bikes:%s, free:%s }' % \
    (self.idx, self.name, self.coordinates, self.lat, self.lng, self.lat, self.lng, self.timestamp, self.bikes, self.free)
    return text.encode('utf-8')

  def from_xml(self, placemark):
    """
    Set the values of the fields from an XML placemark node.

    @param placemark: the XML node containing the data about the station
    @type placemark:  L{xml.dom.minidom.Element}
    """
    description = placemark.getElementsByTagName('description')[0]
    xml = description.firstChild.nodeValue
    dom = minidom.parseString(xml.encode('utf-8'))
    divs = dom.firstChild.getElementsByTagName('div')
    self.name = divs[0].firstChild.nodeValue
    self.bikes = int(divs[2].childNodes[0].nodeValue)
    try:
	self.free = int(divs[2].childNodes[2].nodeValue)
    except (ValueError, IndexError, TypeError):
	self.free = 0
    point = placemark.getElementsByTagName('Point')[0]
    self.coordinates = str(point.firstChild.firstChild.nodeValue)
    p = re.compile('[^0-9.,]')
    shit = p.sub('',self.coordinates)
    awesome = shit.split(',')
    self.lat = int(float(awesome[1])*1000000)
    self.lng = int(float(awesome[0])*1000000)
    
  