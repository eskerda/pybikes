# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "velcom"
URL = "http://www.velcom.fr"
CITY = "plainecommune"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(VelcomStation, prefix)

class VelcomStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY