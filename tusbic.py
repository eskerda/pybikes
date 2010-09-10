# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "tusbic"
URL = "http://www.tusbic.es/"

def get_all():
  return jcdecauxstation.get_all(TusbicStation)

class TusbicStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL