# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "bicloo"
URL = "http://www.bicloo.nantesmetropole.fr"

def get_all():
  return jcdecauxstation.get_all(BiclooStation)

class BiclooStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL