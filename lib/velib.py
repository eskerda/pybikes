# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "velib"
URL = "http://www.velib.paris.fr"

def get_all():
  return jcdecauxstation.get_all(VelibStation)

class VelibStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL