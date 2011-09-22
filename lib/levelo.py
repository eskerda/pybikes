# -*- coding: utf-8 -*-

from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "levelo"
URL = "http://www.levelo-mpm.fr"
CITY = "marseille"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(LeveloStation, prefix)

class LeveloStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY