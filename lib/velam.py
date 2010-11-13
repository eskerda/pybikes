# -*- coding: utf-8 -*-

from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "velam"
URL = "http://www.velam.amiens.fr"

def get_all():
  return jcdecauxstation.get_all(VelamStation)

class VelamStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL