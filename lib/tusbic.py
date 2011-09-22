# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "tusbic"
URL = "http://www.tusbic.es"
CITY = "santander"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(TusbicStation, prefix)

class TusbicStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY
