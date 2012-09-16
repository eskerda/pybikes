# -*- coding: utf-8 -*-
from bicincittaold import BicincittaOldStation
import bicincittaold

PREFIX = "rome"
URL = "http://www.bicincitta.com/citta_v3.asp?id=18&pag=2"

def get_all():
  return bicincittaold.get_all(RomeStation)

class RomeStation(BicincittaOldStation):
  prefix = PREFIX
  main_url = URL
