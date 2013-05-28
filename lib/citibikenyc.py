# -*- coding: utf-8 -*-
import urllib,urllib2
import json

from station import Station


PREFIX = "citibikenyc"
URL = "https://citibikenyc.com/"
STATIONS_URL = "stations/json"

def get_all(prefix = ""):
  stations = []
  index = 0
  usock = urllib2.urlopen(prefix+URL+STATIONS_URL)
  data = json.loads(usock.read())
  usock.close()
  for marker in data['stationBeanList']:
    try:
      station = CitibikeNYCStation(index)
      station.from_json(marker)
      index = index + 1
      stations.append(station)
    except Exception as e:
      print e
  return stations
  
class CitibikeNYCStation(Station):
  prefix = PREFIX
    
  def from_json(self, data):
    
    '''
      {
        "id":2026,
        "stationName":"Broadway & W 60 Street",
        "availableDocks":0,
        "totalDocks":0,
        "latitude":40.76915505,
        "longitude":-73.98191841,
        "statusValue":"Planned",
        "statusKey":2,
        "availableBikes":0,
        "stAddress1":"Broadway & W 60 Street",
        "stAddress2":"",
        "city":"",
        "postalCode":"",
        "location":"",
        "altitude":"",
        "testStation":false,
        "lastCommunicationTime":null,
        "landMark":""
      }
    '''
    if data['statusValue'] == 'Planned':
      raise Exception('Station is only Planned')
    self.name = data['stationName']
    self.bikes = data['availableBikes']
    self.free = data['availableDocks']
    self.number = data['id']
    self.address = data['stAddress1']
    self.lat = int(float(data['latitude'])*1E6)
    self.lng = int(float(data['longitude'])*1E6)
    return self