# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = 'villo'
URL = 'http://www.villo.be'
CITY = "bruxelles"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(VilloStation, prefix)

class VilloStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY