# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = 'valenbisi'
URL = 'http://www.valenbisi.es'

def get_all():
  return jcdecauxstation.get_all(ValenbisiStation)

class ValenbisiStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL