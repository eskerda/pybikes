# -*- coding: utf-8 -*-
import smartbike
from smartbike import SmartBikeCCStation

PREFIX = "bysykler"
URL = "http://smartbikeportal.clearchannel.no"

def get_all(prefix = ""):
  return smartbike.get_all(BysyklerStation, prefix)

class BysyklerStation(SmartBikeCCStation):
  prefix = PREFIX
  url = URL