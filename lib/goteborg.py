# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "goteborg"
URL = "http://www.goteborgbikes.se"
CITY = "goteborg"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(GoteborgStation, prefix)

class GoteborgStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY
