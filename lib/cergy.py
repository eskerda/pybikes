# -*- coding: utf-8 -*-

from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "cergy"
URL = "http://www.velo2.cergypontoise.fr"
CITY = "cergy"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(CergyStation, prefix)

class CergyStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY