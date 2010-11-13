# -*- coding: utf-8 -*-
from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = 'velo'
URL = 'http://www.velo.toulouse.fr'

def get_all():
  return jcdecauxstation.get_all(VeloStation)

class VeloStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL