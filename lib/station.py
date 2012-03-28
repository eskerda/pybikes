# -*- coding: utf-8 -*-

from datetime import datetime
import json

import sys


class StationEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime):
      return obj.isoformat()
    else:
      return obj.__dict__
    return json.JSONEncoder.default(self, obj)

class Station(object):
  prefix = ""
  main_url = ""
  
  def __init__(self,idx):
    self.name = u''
    self.coordinates = ''
    self.lat = 0
    self.lng = 0
    self.bikes = 0
    self.free = 0
    self.timestamp = datetime.now()
    self.number = 0
    self.id = idx
    self.idx = idx
    
  def __str__(self):
    return "name: "+self.name+"\nlat: "+str(self.lat)+"\nlng: "+\
    str(self.lng)+"\nbikes: "+str(self.bikes)+"\nfree: "+str(self.free)+\
    "\ntimestamp: "+str(self.timestamp)+"\nnumber: "+str(self.number)+\
    "\nidx: "+str(self.idx)
	
  def get_prefix(self):
    return self.prefix
    
    
  def to_json(self):
    text = '{"id":"%s", "name":"%s", "lat":"%s", "lng":"%s", "timestamp":"%s", "bikes":%d, "free":%d}' % \
    (self.idx, self.name, self.lat, self.lng, self.timestamp, int(self.bikes), int(self.free))
    return text.encode('utf-8')
