# -*- coding: utf-8 -*-
from bcycle import BCycleStation
import bcycle

PREFIX = "hawaii"
URL = "http://hawaii.bcycle.com/"



def get_all():
  return bcycle.get_all(HawaiiStation)

class HawaiiStation(BCycleStation):
  prefix = PREFIX
  main_url = URL