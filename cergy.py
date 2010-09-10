# -*- coding: utf-8 -*-

from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "cergy"
URL = "http://www.velo2.cergypontoise.fr"

def get_all():
  return jcdecauxstation.get_all(CergyStation)

class CergyStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL