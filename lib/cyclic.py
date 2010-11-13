# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "cyclic"
URL = "http://cyclic.rouen.fr"

def get_all():
  return jcdecauxstation.get_all(CyclicStation)

class CyclicStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL