# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = 'bicikelj'
URL = 'http://en.bicikelj.si/'
CITY = "ljubljana"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(BicikeljStation, prefix)

class BicikeljStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY