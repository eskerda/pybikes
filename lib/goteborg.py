# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "goteborg"
URL = "http://www.goteborgbikes.se"

def get_all():
  return jcdecauxstation.get_all(GoteborgStation)

class GoteborgStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
