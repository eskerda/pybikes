# -*- coding: utf-8 -*-
"""PyBikes
PyBikes is a parsing library to extract bike sharing information from multiple
sources. It contains multiple classes to handle this sort of information,
and is not a class itself. The idea is to be able to call it like:

from pybikes import BicingShareSystem, BicingStation

bicing = new BicingShareSystem() <- Returns BicingShareSystem
print "%s: %s" % ("Bicing City is", bicing.meta.city)
stations = bicing.get_stations() <- Returns Array[BicingStation]

Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import json

from .base import *
from .bixi import *
from .bcycle import *

__all__ = base.__all__ + bixi.__all__ + bcycle.__all__

def getBikeShareSystem(tag, data_file):
    f = open(data_file)
    data = json.loads(f.read())
    meta_data = list(filter(lambda system: system['tag'] == tag, data['instances']))[0]
    return eval(data.get('class'))(** meta_data)
