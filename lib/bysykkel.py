# -*- coding: utf-8 -*-
import smartbike
from smartbike import SmartBikeCCStation

PREFIX = "bysykkel"
URL = "http://smartbikeportal.clearchannel.no"

def get_all(prefix = ""):
  return smartbike.get_all(BysykkelStation, prefix)

class BysykkelStation(SmartBikeCCStation):
  prefix = PREFIX
  url = URL
