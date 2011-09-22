# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "velocite"
URL = "http://www.velocite.besancon.fr"
CITY = "besancon"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(VelociteStation, prefix)

class VelociteStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY