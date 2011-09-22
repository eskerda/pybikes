# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "dublin"
URL = "http://www.dublinbikes.ie"
CITY = "dublin"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(DublinStation, prefix)

class DublinStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY