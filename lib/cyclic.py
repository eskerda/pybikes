# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "cyclic"
URL = "http://cyclic.rouen.fr"
CITY = "rouen"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(CyclicStation, prefix)

class CyclicStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY
