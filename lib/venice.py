# -*- coding: utf-8 -*-
from bicincittanew import BicincittaNewStation
import bicincittanew

PREFIX = "venice"
URL = "http://bicincitta.tobike.it/frmLeStazioni.aspx?ID=93"

def get_all():
  return bicincittanew.get_all(VeniceStation)

class VeniceStation(BicincittaNewStation):
  prefix = PREFIX
  main_url = URL
