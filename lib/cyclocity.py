# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "cyclocity"
URL = "http://www.cyclocity.jp"
CITY = "toyama"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(CyclocityStation, prefix)

class CyclocityStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY
