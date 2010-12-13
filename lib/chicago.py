# -*- coding: utf-8 -*-
from bcycle import BCycleStation
import bcycle

PREFIX = "chicago"
URL = "http://chicago.bcycle.com/"



def get_all():
  return bcycle.get_all(ChicagoStation)

class ChicagoStation(BCycleStation):
  prefix = PREFIX
  main_url = URL