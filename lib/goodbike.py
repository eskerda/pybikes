# -*- coding: utf-8 -*-
from bicincittanew import BicincittaNewStation
import bicincittanew

PREFIX = "goodbike"
URL = "http://www.goodbikepadova.it/frmLeStazioni.aspx"
city="padova"

def get_all():
  return bicincittanew.get_all(GoodBikeStation)

class GoodBikeStation(BicincittaNewStation):
  prefix = PREFIX
  main_url = URL
