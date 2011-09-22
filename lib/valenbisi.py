# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = 'valenbisi'
URL = 'http://www.valenbisi.es'
CITY = "valence"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(ValenbisiStation, prefix)

class ValenbisiStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY
