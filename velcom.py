# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "velcom"
URL = "http://www.velcom.fr"

def get_all():
  return jcdecauxstation.get_all(VelcomStation)

class VelcomStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL