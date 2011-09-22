# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "velib"
URL = "http://www.velib.paris.fr"
CITY = "paris"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(VelibStation, prefix)

class VelibStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY