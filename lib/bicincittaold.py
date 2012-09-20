# -*- coding: utf-8 -*-
from station import Station

import re
import urllib,urllib2

USERAGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1'
HEADERS = {'User-Agent': USERAGENT}


RE_INFO_LAT_CORD="var sita_x =(.*?);"
RE_INFO_LNG_CORD="var sita_y =(.*?);"
RE_INFO_NAME="var sita_n =(.*?);"
RE_INFO_AVAIL="var sita_b =(.*?);"

def clean_raw(raw_string):
    raw_string = raw_string.strip();
    raw_string = raw_string.replace("+","");
    raw_string = raw_string.replace("\"","");
    return raw_string.split("_");


def get_all(spec):
    req = urllib2.Request(spec.main_url, headers=HEADERS)
    usock = urllib2.urlopen(req)
    data = usock.read()
    usock.close()
    
    raw_lat = re.findall(RE_INFO_LAT_CORD,data);
    raw_lng = re.findall(RE_INFO_LNG_CORD,data);
    raw_name =re.findall(RE_INFO_NAME,data);
    raw_avail = re.findall(RE_INFO_AVAIL,data);
    
    vec_lat = clean_raw(raw_lat[0]);
    vec_lng = clean_raw(raw_lng[0]);
    vec_name = clean_raw(raw_name[0]);
    vec_avail = clean_raw(raw_avail[0]);
	
    stations = []
    
    for idx,name in enumerate(vec_name):
        station = spec(idx)
        station.fromData(name,"",int(float(vec_lat[idx])*1E6),int(float(vec_lng[idx])*1E6),int(vec_avail[idx].count("4")),int(vec_avail[idx].count("0")))
        stations.append(station);

    return stations

class BicincittaOldStation(Station):
  prefix = ""
  main_url = ""

  def fromData(self, name, description, lat, lng, bikes, free):
      self.name = name
      self.description = description
      self.lat = lat
      self.lng = lng
      self.bikes = bikes
      self.free = free
      return self

  def update(self):
    return self

  def to_json(self):
    text =  '{"id":"%s", "name":"%s", "lat":"%s", "lng":"%s", "timestamp":"%s", "bikes":%s, "free":%s, "description":"%s"}' % \
    (self.idx, self.name, self.lat, self.lng, self.timestamp, self.bikes, self.free, self.description)
    return unicode(text.decode('iso-8859-15'))
