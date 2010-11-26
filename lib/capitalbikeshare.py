# -*- coding: utf-8 -*-
from bixi import BixiStation
import bixi

PREFIX = "capitalbikeshare"
URL = "http://capitalbikeshare.com/stations/bikeStations.xml"



def get_all():
  return bixi.get_all(CapitalBikeShareStation)

class CapitalBikeShareStation(BixiStation):
  prefix = PREFIX
  main_url = URL