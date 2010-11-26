#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys,os

sys.path.append("lib/")

import valenbisi
import sevici
import dublin
import cyclocity
import bizi
import velib
import velo
import veloh
import villo
import bicing
import cristolib
import cyclic
import velostanlib
import bicloo
import velocite
import barclays
import ecobici

import tusbic
import goteborg
import citycycle
import wien
import velcom
import mulhouse
import levelo
import cergy
import vhello
import velam

import velov

import bixi

import melbourne

import girocleta

import capitalbikeshare

import decobike

import memcache
import time
import subprocess

EXPIRY = 2500000
not_update = ["bicing","barclays","wien","bixi","melbourne","girocleta","capitalbikeshare","decobike"]

def populate(system):
  try:
    stations = system.get_all()
    n_stations = len(stations)
    cache = memcache.Client(['127.0.0.1:11211'])
    system_str = stations[0].prefix
    for station in stations:
      cache.set(station.prefix+"_"+"station_"+str(station.idx),station,EXPIRY)
      print "Added to memcache station "+station.prefix+" "+str(station.idx)
    cache.set(system_str+"_n_stations",n_stations,EXPIRY)
    return n_stations
  except Exception as inst:
    print "Error Populating, Sleeping and retrying!"
    print type(inst)
    time.sleep(5)
    return populate(system)
    
    
def multiupdate(system,fr,to):
  cache = memcache.Client(["127.0.0.1:11211"])
  while True:
    for i in range(fr,to+1):
	try:
		station = cache.get(system+"_station_"+str(i))
		station.update()
		cache.set(system+"_station_"+str(i),station,EXPIRY)
		print "Updated station "+str(station.idx)
	except Exception:
		print "Error getting station "+str(station.idx)
	time.sleep(1)
  
def main(argv):
  if str(argv[0])=="stats":
    print "STATS ARE AWESOME!"
  elif str(argv[0])=="system":
    system_str = str(argv[1])
    system = eval(system_str)
    if (str(argv[2]))=="populate":
      populate(system)
    elif (str(argv[2]))=="multiupdate":
      if (system_str in not_update):
	while True:
	  populate(system)
	  time.sleep(30)
      else:
	multiupdate(system_str,int(argv[3]),int(argv[4]))
    elif str(argv[2])=="all":
      procs = int(argv[3])
      n_stations = populate(system)
      print str(n_stations)
      stat_proc = n_stations/procs
      rest = n_stations%procs
      init_stat = 0
      for i in range(procs):  
	if (init_stat + stat_proc) >= n_stations:
	  to = n_stations-1
	  fr = init_stat
	elif rest > 0:
	  to = init_stat + stat_proc
	  rest = rest - 1
	  fr = init_stat
	  init_stat += stat_proc + 1
	else:
	  to = init_stat + stat_proc - 1
	  fr = init_stat
	  init_stat += stat_proc
	args = ['/usr/bin/python','threader.py','system',system_str,'multiupdate',str(fr), str(to)]
	subprocess.Popen(args)
	
    elif str(argv[2])=="json":
	cache = memcache.Client(["127.0.0.1:11211"])
      	n_stations = cache.get(system_str+"_n_stations")
      	sys.stdout.write('[')
      	for i in range(n_stations):
		station = cache.get(system_str+"_station_"+str(i))
		station.to_json()
		if (i+1!=n_stations):
	  		sys.stdout.write(',')
      	sys.stdout.write(']')
if __name__ == "__main__" :
    main(sys.argv[1:])
