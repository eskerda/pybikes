# -*- coding: utf-8 -*-
from bicincittanew import BicincittaNewStation
import bicincittanew

PREFIX = "tobike"
URL = "http://www.tobike.it/frmLeStazioni.aspx?ID={id}"
COMUNES = [
  {
    'id': 22,
    'name': 'Torino'
  },
  {
    'id': 61,
    'name': 'Grugilasco'
  },
  {
    'id': 62,
    'name': 'Collegno'
  },
  {
    'id': 63,
    'name': 'Venaria Reale'
  },
  {
    'id': 64,
    'name': 'Alpignano'
  },
  {
    'id': 65,
    'name': 'Druento'
  }
]

def get_all():
  stations = []
  st_range = 0
  for comune in COMUNES:
    spec = TOBikeStation
    spec.main_url = URL.format(id = comune['id'])
    comune_stations = bicincittanew.get_all(TOBikeStation, st_range)
    st_range += len(comune_stations)
    stations += comune_stations
  return stations

class TOBikeStation(BicincittaNewStation):
  prefix = PREFIX
  main_url = URL
