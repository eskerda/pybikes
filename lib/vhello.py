# -*- coding: utf-8 -*-

from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "vhello"
URL = "http://www.vhello.fr"

def get_all():
  return jcdecauxstation.get_all(VhelloStation)

class VhelloStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL