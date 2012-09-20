# -*- coding: utf-8 -*-
from bicincittanew import BicincittaNewStation
import bicincittanew

PREFIX = "tigullionbike"
URL = "http://bicincitta.tobike.it/frmLeStazioni.aspx?ID=80"

def get_all():
  return bicincittanew.get_all(TigullionbikeStation)

class TigullionbikeStation(BicincittaNewStation):
  prefix = PREFIX
  main_url = URL
