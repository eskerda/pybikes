# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = 'sevici'
URL = 'http://www.sevici.es'

def get_all():
  return jcdecauxstation.get_all(SeviciStation)

class SeviciStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL