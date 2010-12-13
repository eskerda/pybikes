# -*- coding: utf-8 -*-
from bcycle import BCycleStation
import bcycle

PREFIX = "desmoines"
URL = "http://desmoines.bcycle.com/"



def get_all():
  return bcycle.get_all(DesMoinesStation)

class DesMoinesStation(BCycleStation):
  prefix = PREFIX
  main_url = URL