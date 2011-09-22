# -*- coding: utf-8 -*-

from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "mulhouse"
URL = "http://www.velocite.mulhouse.fr"
CITY = "mulhouse"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(MulhouseStation, prefix)

class MulhouseStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY