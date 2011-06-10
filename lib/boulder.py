# -*- coding: utf-8 -*-
from bcycle import BCycleStation
import bcycle

PREFIX = "boulder"
URL = "http://boulder.bcycle.com/"



def get_all():
  return bcycle.get_all(BoulderStation)

class BoulderStation(BCycleStation):
  prefix = PREFIX
  main_url = URL