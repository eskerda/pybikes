__version__ = "1.0.0.dev0"

# Top class shortcuts #####################
from pybikes.data import get
from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper

# Compat old methods
from pybikes.data import get_data, get_all_data, get_schemas
from pybikes.data import get_instances, get_system_cls, get_instance
from pybikes.data import find_system
from pybikes.data import getBikeShareSystem, getDataFile, getDataFiles
###########################################
