# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = 'veloh'
URL = 'http://www.veloh.lu'

def get_all():
  return jcdecauxstation.get_all(VelohStation)

class VelohStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL