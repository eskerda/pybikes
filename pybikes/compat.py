import re
import json

from pkg_resources import resource_string, resource_listdir

from pybikes.data import get, find, _datafile_traversor, _import
from pybikes.exceptions import BikeShareSystemNotFound


def get_data(schema):
    resource = resource_string('pybikes', 'data/%s.json' % schema)
    return json.loads(resource)


def get_all_data():
    return resource_listdir('pybikes', 'data')


def get_schemas():
    return [re.sub(r'\.json$', '', name) for name in get_all_data()]


def get_instances(schema=None):
    schemas = [schema] or get_schemas()
    for schema in schemas:
        data = get_data(schema)
        instances = data.get('instances')
        for cls, instance in _datafile_traversor(data['class'], instances):
            yield cls, instance


def get_system_cls(schema, cname):
    mod = _import('pybikes.%s' % schema)
    return getattr(mod, cname)


def get_instance(schema, tag):
    for cname, instance in get_instances(schema):
        if instance['tag'] == tag:
            return cname, instance

    msg = 'System %s not found in schema %s' % (tag, schema)
    raise BikeShareSystemNotFound(msg)


def find_system(tag):
    mod_name, cls_name, i_data = find(tag)

    return cls_name, i_data

def getBikeShareSystem(system, tag, key=None):
    return get(tag, key)


def getDataFile(schema):
    return get_data(schema)


def getDataFiles():
    return get_all_data()
