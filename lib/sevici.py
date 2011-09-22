# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = 'sevici'
URL = 'http://www.sevici.es'
CITY = "seville"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(SeviciStation, prefix)

class SeviciStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY
