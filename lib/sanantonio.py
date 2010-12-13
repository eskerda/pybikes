# -*- coding: utf-8 -*-
from bcycle import BCycleStation
import bcycle

PREFIX = "sanantonio"
URL = "http://sanantonio.bcycle.com/"



def get_all():
  return bcycle.get_all(SanAntonioStation)

class SanAntonioStation(BCycleStation):
  prefix = PREFIX
  main_url = URL