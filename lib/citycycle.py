# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "citycycle"
URL = "http://www.citycycle.com.au"
CITY = "brisbane"

def get_all(prefix = ""):
  return jcdecauxstation.get_all(CityCycleStation, prefix)

class CityCycleStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL
  city = CITY
