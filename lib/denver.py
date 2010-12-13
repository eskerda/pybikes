# -*- coding: utf-8 -*-
from bcycle import BCycleStation
import bcycle

PREFIX = "denver"
URL = "http://denver.bcycle.com/"



def get_all():
  return bcycle.get_all(DenverStation)

class DenverStation(BCycleStation):
  prefix = PREFIX
  main_url = URL