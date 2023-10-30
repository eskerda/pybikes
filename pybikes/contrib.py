import re
import time
import inspect

try:
    # Python 2
    from itertools import imap as map
except ImportError:
    # Python 3
    pass

from pybikes import BikeShareSystem, BikeShareStation


class TSTCache(dict):
    """ TSTCache stands for TimeStamped Test Cache

    This class provides an implementation of a dict that only adds values
    depending on a test function that should be overriden (always true by
    default).

    It is timestamped because data is added with a timestamp. When timedelta is
    greater than a predefined delta it will also return None
    """

    def __init__(self, store=None, delta=60, *args, **kwargs):
        if store is None:
            store = {}
        self.store = store
        self.delta = delta
        self.update(dict(*args, **kwargs))

    def __setitem__(self, key, value):
        key = self.__transform_key__(key)
        if not self.__test_key__(key):
            return

        self.store[key] = self.__transform_value__(key, value)

    def __getitem__(self, key):
        key = self.__transform_key__(key)
        if not self.__test_key__(key):
            raise KeyError('%s' % key)
        if key not in self.store:
            raise KeyError('%s' % key)
        ts_value = self.store[key]
        the_time = time.time()

        if the_time - ts_value['ts'] > self.__get_delta__(key, ts_value):
            raise KeyError('%s' % key)

        return ts_value['value']

    def __contains__(self, key):
        key = self.__transform_key__(key)
        try:
            self[key]
        except Exception:
            return False
        return True

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def get(self, key, default=None):
        return self[key] if key in self else default

    def items(self):
        return ((k, self[k]) for k, v in self.store.items() if k in self)

    def keys(self):
        return (k for k in self.store.keys() if k in self)

    def __test_key__(self, key):
        return True

    def __transform_key__(self, key):
        return key

    def __transform_value__(self, key, value):
        return {
            'value': value,
            'ts': time.time(),
        }

    def __get_delta__(self, key, entry):
        return self.delta

    def __repr__(self):
        return self.store.__repr__()

    def flush(self):
        for k, v in list(self.store.items()):
            if k in self:
                continue
            del self.store[k]


class PBCache(TSTCache):
    """ PBCache stands for PyBikes Cache

    It's the same as the TSTCache, but annotates entries with callstack
    information based on being called from a bike share system

    Gets initialized with a list of defined deltas per regex rule. Said
    delta will be aplied to entries based on its annotation.
    """

    def __init__(self, * args, deltas=None, ** kwargs):
        super(PBCache, self).__init__(* args, ** kwargs)
        self.deltas = deltas or []

    def __get_annotation__(self, key):
        """ introspect call stack to find a bike share system """
        valid_types = (BikeShareSystem, )
        stack = inspect.stack()
        selfs = map(lambda f: (f.frame.f_locals.get('self'), f), stack)
        bss = filter(lambda f: isinstance(f[0], valid_types), selfs)

        some_bikeshare, frame_info = next(bss, (None, None))

        # no bike share found on call stack, bail
        if not some_bikeshare:
            return None

        # create an annotation based on bike share found
        # ie: 'gbfs::citi-bike-nyc::update::https://some-url'
        annotation = '{cls}::{tag}::{method}::{key}'.format(
            cls=some_bikeshare.__class__.__name__.lower(),
            tag=some_bikeshare.tag,
            method=frame_info.function,
            key=key,
        )

        return annotation

    def __match_delta__(self, key):
        annotation = self.__get_annotation__(key)

        if not annotation:
            return None, None

        # get a delta value based on annotation
        # list of deltas are a list of dicts like
        #   - it's a list because it keeps order
        #   - it's made of dicts because it's a safe json structure
        # [
        #   {'gbfs::.*::update': 100},
        #   {'gbfs::some-tag::update::some-url': 200},
        # ]

        # iterate items on delta list
        deltas = map(lambda e: e.items(), self.deltas)
        # flatten iterator
        deltas = (e for it in deltas for e in it)
        apply_rules = filter(lambda r: re.match(r[0], annotation), deltas)
        _, delta = next(apply_rules, (None, self.delta))

        return delta, annotation

    def __transform_value__(self, key, value):
        delta, annotation = self.__match_delta__(key)
        return {
            'value': value,
            'ts': time.time(),
            'delta': delta,
            'annotation': annotation,
        }

    def __get_delta__(self, key, entry):
        delta = entry.get('delta')
        # guards against a delta = 0 triggering return of self.delta
        return delta if delta is not None else self.delta

    def set_with_delta(self, key, value, delta):
        entry = self.__transform_value__(key, value)
        entry['delta'] = delta
        self.store[key] = entry
