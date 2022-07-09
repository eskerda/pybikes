import sys
import json

from pybikes.exceptions import BikeShareSystemNotFound

from importlib import import_module

from pkg_resources import resource_string, resource_listdir


def _iter_data():
    for data_file in resource_listdir('pybikes', 'data'):
        resource = resource_string('pybikes', 'data/%s' % data_file)
        yield data_file, json.loads(resource)


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
