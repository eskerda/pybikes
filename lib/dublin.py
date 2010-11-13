# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "dublin"
URL = "http://www.dublinbikes.ie"

def get_all():
  return jcdecauxstation.get_all(DublinStation)

class DublinStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL