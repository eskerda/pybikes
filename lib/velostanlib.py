# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "velostanlib"
URL = "http://www.velostanlib.fr"
CITY = "nancy"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(VelostanlibStation, prefix)

class VelostanlibStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY
