#!/usr/bin/python2.7
# -*- coding: utf-8 -*-


import sys,os

full_path = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append("%s/lib" % full_path)

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

import niceride

import chicago
import denver
import desmoines
import sanantonio
import hawaii
import nextbike

import tobike

import bicikelj

import bikemi
import hangzhou
import boulder

import memcache
import time
import subprocess


import urllib, urllib2
from datetime import datetime

EXPIRY = 2500000
not_update = ["bicing","barclays","wien","bixi","melbourne","girocleta","capitalbikeshare","decobike","niceride","chicago","denver","desmoines","sanantonio","nextbike","tobike","hawaii","svd","hangzhou","boulder","bikemi"]
def populate(system):
  try:
    stations = system.get_all()
  except Exception:
    try:
	print "[%s]Error populating %s, trying tor" % (datetime.now(),system.__name__)
	stations = system.get_all("http://api.citybik.es/torify/")
    except Exception:
    	print "Fatal error, sleeping and retrying"
    	time.sleep(60)
    	return populate(system)
  n_stations = len(stations)
  cache = memcache.Client(['127.0.0.1:11211'])
  if system == nextbike:
    pfx = None
    for station in stations:
      if pfx != station.prefix:
	if pfx is not None:
	  cache.set(pfx+"_n_stations",ct,EXPIRY)
	ct = 0
	pfx = station.prefix
      cache.set(station.prefix+"_"+"station_"+str(station.idx),station,EXPIRY)
      print "Added to memcache station "+station.prefix+" "+str(station.idx)
      ct = ct + 1
    return n_stations
  else:
    system_str = stations[0].prefix
    for station in stations:
      cache.set(station.prefix+"_"+"station_"+str(station.idx),station,EXPIRY)
    cache.set(system_str+"_n_stations",n_stations,EXPIRY)
    print "[%s]Added to memcache %d %s stations" % (datetime.now(),n_stations,system.__name__)
    return n_stations
    
    
def multiupdate(system,fr,to):
  cache = memcache.Client(["127.0.0.1:11211"])
  while True:
    for i in range(fr,to+1):
	station = cache.get(system+"_station_"+str(i))
	try:
	  station.update()
	except Exception:
	  print "[%s]Error getting %s station %d trying Tor" % (datetime.now(), system, station.idx)
	  try:
	    station.update("http://api.citybik.es/torify/")
	    print "[%s]Tor went okay.. %s %d" % (datetime.now(), system, station.idx)
	    time.sleep(0.5)
	  except Exception:
	    print "[%s]Fatal Error getting %s station %d" % (datetime.now(), system, station.idx)
	    time.sleep(8)
	    continue
	cache.set(system+"_station_"+str(i),station,EXPIRY)
  	time.sleep(0.5)

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
      if len(argv) > 4:
	no_update = int(argv[4])
      else:
	no_update = 0
      if no_update > 0:
	print "Not cleaning %s station list" % system_str
	cache = memcache.Client(["127.0.0.1:11211"])
      	n_stations = cache.get(system_str+"_n_stations")
      	if n_stations is None:
	  print "It not went ok %s, repopulating" % system_str
	  n_stations = populate(system)
      else:
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
	args = ['%s/fast.py' % full_path,'system',system_str,'multiupdate',str(fr), 
str(to)]
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
