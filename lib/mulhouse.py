# -*- coding: utf-8 -*-

from jcdecauxstation import JCDecauxStation
import jcdecauxstation

PREFIX = "mulhouse"
URL = "http://www.velocite.mulhouse.fr"

def get_all():
  return jcdecauxstation.get_all(MulhouseStation)

class MulhouseStation(JCDecauxStation):
  prefix = PREFIX
  main_url = URL