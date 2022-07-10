# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

__author__ = "eskerda (eskerda@gmail.com)"
__version__ = "2.0"
__copyright__ = "Copyright (c) 2010-2012 eskerda"
__license__ = "AGPL"

# Top class shortcuts #####################
from pybikes.data import get
from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper

# Compat old methods
from pybikes.compat import get_data, get_all_data, get_schemas
from pybikes.compat import get_instances, get_system_cls, get_instance
from pybikes.compat import find_system
from pybikes.compat import getBikeShareSystem, getDataFile, getDataFiles
###########################################
