# -*- coding: utf-8 -*-

from station import Station
from BeautifulSoup import BeautifulStoneSoup
import urllib,urllib2
from datetime import datetime

PREFIX = 'vlille'
LIST_URL = '/stations/xml-stations.aspx'
STATION_URL = '/stations/xml-station.aspx?borne='


def get_all():
  usock = urllib2.urlopen(VLille.main_url+LIST_URL)
  xml_data = usock.read()
  usock.close()
  soup = BeautifulStoneSoup(xml_data)
  markers = soup.findAll('marker')
  stations = []
  for index, marker in enumerate(markers):
    station = VLille(index)
    station.from_xml(marker.prettify())
    stations.append(station)
  return stations

class VLille(Station):
  prefix = PREFIX
  main_url = "http://vlille.fr"
  station_url = STATION_URL

  def update(self):
    usock = urllib.urlopen(self.main_url + self.station_url + str(self.number))
    xml_data = usock.read()
    usock.close()
    soup = BeautifulStoneSoup(xml_data)
    self.bikes = int(soup.find('bikes').contents[0])
    self.free = int(soup.find('attachs').contents[0])
    self.timestamp = datetime.now()
    return self

  def from_xml(self, xml_data):
    soup = BeautifulStoneSoup(xml_data)
    self.number = int(soup.contents[0].get("id"))
    self.name = unicode(BeautifulStoneSoup(soup.contents[0].get("name"),convertEntities=BeautifulStoneSoup.HTML_ENTITIES )).replace('\n','')
    if (self.name == ""):
      self.name = "??"
    self.lat = int(float(soup.contents[0].get("lat"))*1E6)
    self.lng = int(float(soup.contents[0].get("lng"))*1E6)

