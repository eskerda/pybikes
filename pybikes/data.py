import re
import sys
import json

from importlib import import_module

from pybikes.exceptions import BikeShareSystemNotFound
from pybikes.compat import resources


def _iter_data():
    for file in (resources.files('pybikes')/'data').iterdir():
        yield file.name, json.loads(file.read_bytes())


def _import(name):
    if name in sys.modules:
        return sys.modules[name]

    return import_module(name)


def _datafile_traversor(cls, instances):
    # multiclass
    if isinstance(cls, dict):
        for k, v in cls.items():
            for x in _datafile_traversor(k, v.get('instances', [])):
                yield x
        return

    # single class
    for instance in instances:
        yield cls, instance


def _traverse_lib():
    for fname, data in _iter_data():
        instances = data.get('instances')
        for cls, instance in _datafile_traversor(data['class'], instances):
            yield data['system'], cls, instance


# traverse library only once
_traversor = _traverse_lib()
_t_cache = {}
def find(tag):
    if tag in _t_cache:
        return _t_cache[tag]

    for mod_name, cls_name, i_data in _traversor:
        _t_cache[i_data['tag']] = mod_name, cls_name, i_data

        if i_data['tag'] == tag:
            return mod_name, cls_name, i_data

    raise BikeShareSystemNotFound("System '%s' not found" % tag)


def get(tag, key=None):
    mod_name, cls_name, i_data = find(tag)

    mod = _import('pybikes.%s' % mod_name)
    cls = getattr(mod, cls_name)

    if cls.authed:
        if not key:
         raise Exception('System %s needs a key to work' % cls_name)

        return cls(key=key, **i_data)

    return cls(**i_data)


# compatibility with old methods ####################################

def get_data(schema):
    resource = resources.files('pybikes') / ('data/%s.json' % schema)
    return json.loads(resource.read_bytes())


def get_all_data():
    return [f.name for f in (resources.files('pybikes') / 'data').iterdir()]


def get_schemas():
    return [re.sub(r'\.json$', '', name) for name in get_all_data()]


def get_instances(schema=None):
    schemas = [schema] if schema else get_schemas()
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

####################################################################
