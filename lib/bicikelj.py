# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = 'bicikelj'
URL = 'http://en.bicikelj.si'

def get_all():
  return jcdecauxstation.get_all(BicikeljStation)

class BicikeljStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
