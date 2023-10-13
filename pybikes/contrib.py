import time


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
        self.store[key] = {
            'value': value,
            'ts': time.time()
        }

    def __getitem__(self, key):
        key = self.__transform_key__(key)
        if not self.__test_key__(key):
            raise KeyError('%s' % key)
        if key not in self.store:
            raise KeyError('%s' % key)

        ts_value = self.store[key]
        the_time = time.time()
        delta = ts_value.get('delta', self.delta)

        if the_time - ts_value['ts'] > delta:
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

    def __test_key__(self, key):
        return True

    def __transform_key__(self, key):
        return key

    def set_with_delta(self, key, value, delta):
        """ Set a key-value with a specific delta """
        self.store[key] = {
            'value': value,
            'ts': time.time(),
            'delta': delta,
        }
