# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "cristolib"
URL = "http://www.cristolib.fr"
CITY = "creteil"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(CristolibStation, prefix)

class CristolibStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY