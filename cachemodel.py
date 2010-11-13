#!/bin/env python
# -*- coding: utf-8 -*-

import memcache

systems = ['valenbisi','sevici','dublin','cyclocity','bizi',\
	   'velib','velo','veloh','villo','bicing',\
	   'cristolib','cyclic','velostanlib','bicloo','velocite',\
	   'barclays','ecobici','tusbic','goteborg','citycycle',\
	   'wien','velcom','mulhouse','levelo','cergy',\
	   'vhello','velam','velov','bixi','melbourne','girocleta']

cache = memcache.Client(['127.0.0.1:11211'])


def _test_system(system):
  return str(system) in systems
  
def get_station(system, idx):
  if _test_system(system):
    return cache.get(str(system)+"_station_"+str(idx))
  else:
    return None

def get_all(system):
  if _test_system(system):
    n_stations = cache.get(str(system)+"_n_stations")
    if n_stations is None:
      n_stations = 0
    stations = []
    for i in range(n_stations):
      station = get_station(system, i)
      stations.append(station)
    return stations
  else:
    return None
