# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = 'velo'
URL = 'http://www.velo.toulouse.fr'
CITY = "toulouse"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(VeloStation, prefix)

class VeloStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY
