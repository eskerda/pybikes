# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "cyclocity"
URL = "http://www.cyclocity.jp"

def get_all():
  return jcdecauxstation.get_all(CyclocityStation)

class CyclocityStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL