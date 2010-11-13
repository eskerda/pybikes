# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "velocite"
URL = "http://www.velocite.besancon.fr"

def get_all():
  return jcdecauxstation.get_all(VelociteStation)

class VelociteStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL