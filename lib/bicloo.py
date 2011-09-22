# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "bicloo"
URL = "http://www.bicloo.nantesmetropole.fr"
CITY = "nantes"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(BiclooStation, prefix)

class BiclooStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY