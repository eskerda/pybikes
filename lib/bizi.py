# -*- coding: utf-8 -*-
from station import Station

import re
import urllib,urllib2
from BeautifulSoup import BeautifulSoup
from datetime import datetime

PREFIX = "bizi"
URL = "http://www.bizizaragoza.com"
LIST_URL = "/localizaciones/localizaciones.php"
STATION_URL = "/CallWebService/StationBussinesStatus.php"

LAT_LNG_RGX = 'point \= new GLatLng\((.*?)\,(.*?)\)'
ID_ADD_RGX = 'idStation\=\"\+(.*)\+\"\&addressnew\=(.*)\"\+\"\&s\_id\_idioma'


def getStats(txt):
  re1='.*?'	# Non-greedy match on filler
  re2='\\d+'	# Uninteresting: int
  re3='.*?'	# Non-greedy match on filler
  re4='(\\d+)'	# Integer Number 1
  re5='.*?'	# Non-greedy match on filler
  re6='(\\d+)'	# Integer Number 2

  rg = re.compile(re1+re2+re3+re4+re5+re6,re.IGNORECASE|re.DOTALL)
  m = rg.search(txt)
  if m:
    int1=m.group(1)
    int2=m.group(2)
    res = [int1,int2]
    return res
    
    
def get_all():
  usock = urllib2.urlopen(URL+LIST_URL)
  data = usock.read()
  usock.close()

  geopoints = re.findall(LAT_LNG_RGX, data)
  ids_addrs = re.findall(ID_ADD_RGX, data)
  
  stations = []
  for index,geopoint in enumerate(geopoints):
    station = BiziStation(index)
    station.lat = int(float(geopoint[0])*1E6)
    station.lng = int(float(geopoint[1])*1E6)
    station.number = int(ids_addrs[index][0])
    station.address = ids_addrs[index][1]
    stations.append(station)
  return stations
  

class BiziStation(Station):
  prefix = PREFIX
  main_url = URL
  address = ""
      
  def update(self):
    print "Updating "+str(self.number)
    parameters = {'idStation':self.number,'addressnew':self.address}
    data = urllib.urlencode(parameters)
    request = urllib2.Request(URL+STATION_URL,data)
    response = urllib2.urlopen(request)
    txt = response.read()
    soup = BeautifulSoup(txt)
    name = soup.div.contents[1].contents[0]
    stats = getStats(soup.div.contents[3].prettify())
    self.name = unicode(BeautifulSoup(name,convertEntities=BeautifulSoup.HTML_ENTITIES )).replace('\n','')
    self.bikes = stats[0]
    self.free = stats[1]
    self.timestamp = datetime.now()  
    return self
