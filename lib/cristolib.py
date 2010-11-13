# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "cristolib"
URL = "http://www.cristolib.fr"

def get_all():
  return jcdecauxstation.get_all(CristolibStation)

class CristolibStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL