# -*- coding: utf-8 -*-
from station import Station

import urllib,urllib2
import re
from datetime import datetime
from xml.dom import minidom


PREFIX = "svd"
HASH_URL = "http://clearchannel.stare-d.se/"
URL = HASH_URL + "ajax/getRacks/%s"

HASH_RGX = 'var hash \= \"(.*?)\"'



def getHash(html):
  hashs = re.findall(HASH_RGX, html)
  return hashs[0]
  
def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
    
    

def get_all():
  usock = urllib2.urlopen(HASH_URL)
  hash_data = usock.read()
  evil_hash = getHash(hash_data)
  usock = urllib2.urlopen(URL % evil_hash)
  xml_data = usock.read()
  usock.close()
  dom = minidom.parseString(xml_data)
  markers = dom.getElementsByTagName('station')
  stations = []
  for index, marker in enumerate(markers):
    station = StockholmStation(index)
    station.from_xml(marker)
    stations.append(station)
  return stations
  
  
class StockholmStation(Station):
  prefix = PREFIX

  def to_json(self):
    text =  '{id:"%s", name:"%s", lat:"%s", lng:"%s", timestamp:"%s", bikes:%s, free:%s, number:"%s", status:"%s", description:"%s"}' % \
    (self.idx, self.name, self.lat, self.lng, self.timestamp, self.bikes, self.free, self.number, self.status, self.description)
    print text.encode('utf-8'),
    return text.encode('utf-8')
  
  def update(self):
    return self
    
  def from_xml(self, xml_data):
    
    """ xml marker object as in
      <racks>
      <station>
      <rack_id>1</rack_id>
      <description>Djurgården Allmänna gränd</description>
      <longitute>18.0948995</longitute>
      <latitude>59.3242468</latitude>
      <ready_bikes>1</ready_bikes>
      <empty_locks>10</empty_locks>
      <last_update>2011-05-09 14:10:02</last_update>
      <online>1</online>
      </station>
      ...
    """
    
    self.number = int(getText(xml_data.getElementsByTagName("rack_id")[0].childNodes))
    self.name = unicode(getText(xml_data.getElementsByTagName("description")[0].childNodes))
    self.lat = int(float(getText(xml_data.getElementsByTagName("latitude")[0].childNodes))*1E6)
    self.lng = int(float(getText(xml_data.getElementsByTagName("longitute")[0].childNodes))*1E6)
    self.bikes = int(getText(xml_data.getElementsByTagName("ready_bikes")[0].childNodes))
    self.free = int(getText(xml_data.getElementsByTagName("empty_locks")[0].childNodes))
    self.status = unicode(getText(xml_data.getElementsByTagName("online")[0].childNodes))
    self.description = unicode(getText(xml_data.getElementsByTagName("description")[0].childNodes))  