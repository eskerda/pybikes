# -*- coding: utf-8 -*-
from bixi import BixiStation
import bixi

PREFIX = "niceride"
URL = "http://secure.niceridemn.org/data2/bikeStations.xml"



def get_all():
  return bixi.get_all(NiceRideStation)

class NiceRideStation(BixiStation):
  prefix = PREFIX
  main_url = URL