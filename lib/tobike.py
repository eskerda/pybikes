# -*- coding: utf-8 -*-
from bicincittanew import BicincittaNewStation
import bicincittanew

PREFIX = "tobike"
URL = "http://www.tobike.it/frmLeStazioni.aspx"

def get_all():
  return bicincittanew.get_all(TOBikeStation)

class TOBikeStation(BicincittaNewStation):
  prefix = PREFIX
  main_url = URL
