# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = 'veloh'
URL = 'http://www.veloh.lu'
CITY = "luxembourg"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(VelohStation, prefix)

class VelohStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY