# -*- coding: utf-8 -*-
import urllib,urllib2
import demjson

from jcdecauxstation import JCDecauxStation
import jcdecauxstation


PREFIX = "velov"
URL = "http://www.velov.grandlyon.com/velovmap/zhp/inc/"
STATIONS_BY_BOROUGH_URL = "StationsParArrondissement.php?arrondissement="
BOROUHS = [69381, 69382, 69383, 69384, 69385, 69386, 69387, 69388, 69389, 69266, 69034, 69256]
STATION_URL = 'DispoStationsParId.php?id='

def get_all():
  stations = []
  index = 0
  for borough in BOROUHS:
    usock = urllib2.urlopen(URL+STATIONS_BY_BOROUGH_URL+str(borough))
    data = usock.read()
    usock.close()
    for marker in demjson.decode(data)['markers']:
      station = VelovStation(index)
      station.from_json(marker)
      index = index + 1
      stations.append(station)
  return stations
  
class VelovStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  station_url = STATION_URL
    
  def from_json(self, json_data):
    ''' {u'y': u'4.920601000000000', u'x': u'45.76081800000000', u'infoStation': u'Rue de la Poudrette', u'nomStation': u'12001 - La Soie', u'numStation': u'12001'} '''
    self.number = int(json_data['numStation'])
    self.name = json_data['nomStation'].encode('utf-8')
    self.lat = int(float(json_data['x'])*1E6)
    self.lng = int(float(json_data['y'])*1E6)
    return self
 
  def to_json(self):
    text =  '{id:"%s", name:"%s", lat:"%s", lng:"%s", timestamp:"%s", bikes:%s, free:%s}' % \
    (self.idx, self.name, self.lat, self.lng, self.timestamp, self.bikes, self.free)
    print text,
    return text