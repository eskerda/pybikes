# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = 'villo'
URL = 'http://www.villo.be'

def get_all():
  return jcdecauxstation.get_all(VilloStation)

class VilloStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL