# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "velostanlib"
URL = "http://www.velostanlib.fr"

def get_all():
  return jcdecauxstation.get_all(VelostanlibStation)

class VelostanlibStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL