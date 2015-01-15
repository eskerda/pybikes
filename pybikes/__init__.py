# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

"""PyBikes
PyBikes is a parsing library to extract bike sharing information from multiple
sources. It contains multiple classes to handle this sort of information,
and is not a class itself. The idea is to be able to call it like:

from pybikes import BicingShareSystem, BicingStation

bicing = new BicingShareSystem() <- Returns BicingShareSystem
print "%s: %s" % ("Bicing City is", bicing.meta.city)
stations = bicing.get_stations() <- Returns Array[BicingStation]

"""
__author__ = "eskerda (eskerda@gmail.com)"
__version__ = "2.0"
__copyright__ = "Copyright (c) 2010-2012 eskerda"
__license__ = "AGPL"

import json
import glob
import os

from pkg_resources import resource_string, resource_listdir

from .base import *
from .exceptions import *
from .bixi import *
from .bcycle import *
from .smartbike import *
from .cyclocity import *
from .bicincitta import *
from .domoblue import *
from .gewista_citybike import *
from .decobike import *
from .keolis import *
from .emovity import *
from .bicipalma import *
from .bicicard import *
from .nextbike import *
from .samba import *
from .ciclosampa import *
from .veloway import *
from .easybike import *

__all__ = base.__all__ +\
          bixi.__all__ +\
          bcycle.__all__ +\
          smartbike.__all__+\
          cyclocity.__all__+\
          bicincitta.__all__+\
          domoblue.__all__+\
          gewista_citybike.__all__+\
          decobike.__all__+\
          keolis.__all__+\
          emovity.__all__+\
          bicipalma.__all__+\
          bicicard.__all__+\
          nextbike.__all__+\
          samba.__all__+\
          ciclosampa.__all__+\
          veloway.__all__+\
          easybike.__all__

def getDataFiles():
    return resource_listdir(__name__, 'data')

def getDataFile(system):
    file_info = os.path.splitext(system)
    try:
        return json.loads(
            resource_string(__name__, "data/%s.json" % file_info[0]).decode('utf-8')
        )
    except NameError:
        raise NameError('File data/%s.json not found' % system)

def getBikeShareSystem(system, tag, key = None):
    data = getDataFile(system)
    if isinstance(data.get('class'), unicode):
        return getUniclassBikeShareSystem(system, tag, key)
    elif isinstance(data.get('class'), dict):
        return getMulticlassBikeShareSystem(system, tag, key)
    else:
        raise Exception('Malformed system %s' % system)

def getUniclassBikeShareSystem(system, tag, key = None):
    data = getDataFile(system)
    meta_data = [sys for sys in data['instances'] if sys['tag'] == tag]
    if len(meta_data) == 0:
        raise BikeShareSystemNotFound(
            'System %s not found in data/%s.json' % (tag, system))
    meta_data = meta_data[0]
    system_class = eval(data.get('class'))
    if system_class.authed:
        if key is None:
            raise Exception('System %s needs a key' % system)
        meta_data['key'] = key
    return system_class(** meta_data)

def getMulticlassBikeShareSystem(system, tag, key):
    data = getDataFile(system)
    clss = [cls for cls in data['class']]
    for cls in clss:
        for inst in data['class'][cls]['instances']:
            if tag == inst['tag']:
                syscls = eval(cls)
                if syscls.authed:
                    if key is None:
                        raise Exception('System %s needs a key' % system)
                    inst['key'] = key
                return syscls(** inst)

    raise exceptions.BikeShareSystemNotFound(
        'System %s not found in data/%s.json' % (tag, system))
