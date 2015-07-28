# -*- coding: utf-8 -*-
# Copyright (C) 2015, Eduardo Mucelli Rezende Oliveira <edumucelli@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

import json
import codecs

from lxml import etree

from .base import BikeShareSystem, BikeShareStation
from . import utils, exceptions

__all__ = ['Encicla', 'EnciclaStation']

parse_methods = {
  'json': 'get_json_stations',
}

class Encicla(BikeShareSystem):

  sync = True

  meta = {
    'system': 'Encicla',
    'company': 'Sistema de Bicicletas Públicas del Valle de Aburrá'
  }

  def __init__(self, tag, feed_url, meta, format):
    super(Encicla, self).__init__(tag, meta)
    self.feed_url = feed_url
    self.method = format

  def update(self, scraper = None):
    if scraper is None:
      scraper = utils.PyBikesScraper()

    if self.method not in parse_methods:
      raise Exception(
        'Extractor for method %s is not implemented' % self.method )

    self.stations = eval(parse_methods[self.method])(self, scraper)

def get_json_stations(self, scraper):
  data = json.loads(scraper.request(self.feed_url))
  stations = []
  
  for station in data['stations']:
    for item in station['items']:
      station = EnciclaStation.from_json(item)
      stations.append(station)
  return stations
  
class EnciclaStation(BikeShareStation):
  def __init__(self):
    super(EnciclaStation, self).__init__()

  @staticmethod
  def from_json(data):
    '''
      {
      "order": 0,
      "name": "Moravia",
      "address": "CALLE 82A # 52-29",
      "description": "Frente a la entrada principal del Centro de Desarrollo Cultural de Moravia",
      "lat": "6.276585",
      "lon": "-75.564804",
      "type": "manual",
      "capacity": 15,
      "bikes": 8,
      "places": null,
      "picture": "http:\/\/encicla.gov.co\/wp-content\/uploads\/estaciones-360-moravia.jpg",
      "bikes_state": 0,
      "places_state": "danger",
      "closed": 0,
      "cdo": 0
      }
    '''
    station = EnciclaStation()
    
    station.name      = data['name']
    station.longitude = float(data['lon'])
    station.latitude  = float(data['lat'])
    station.bikes     = int(data['bikes'])
    places            = data['places']
    if places is None:
      # For some stations that present 'null' for the 'places' attribute
      station.free    = int(data['capacity']) - int(data['bikes'])
    else:
      station.free    = int(places)

    # 'bikes_state' may also be a label as 'warning' as well, do not try to cast it to int
    station.extra = {
      'order': int(data['order']),
      'address': data['address'],
      'description': data['description'],
      'type': data['type'],
      'capacity': data['capacity'],
      'picture': data['picture'],
      'bikes_state': data['bikes_state'],
      'places_state': data['places_state'],
      'closed': int(data['closed']),
      'cdo': int(data['cdo'])
    }
    return station
