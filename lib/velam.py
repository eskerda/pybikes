# -*- coding: utf-8 -*-

from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "velam"
URL = "http://www.velam.amiens.fr"
CITY = "amiens"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(VelamStation, prefix)

class VelamStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY