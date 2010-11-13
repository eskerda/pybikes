# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "citycycle"
URL = "http://www.citycycle.com.au"

def get_all():
  return jcdecauxstation.get_all(CityCycleStation)

class CityCycleStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
