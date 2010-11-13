# -*- coding: utf-8 -*-

from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "levelo"
URL = "http://www.levelo-mpm.fr"

def get_all():
  return jcdecauxstation.get_all(LeveloStation)

class LeveloStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL