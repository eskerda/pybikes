import re

try:
    # Python 3
    from unittest.mock import Mock
except ImportError:
    # Python 2
    from mock import Mock


import pytest

import pybikes
from pybikes.data import _traverse_lib

try:
    import keys
except ImportError:
    print("Keys for testing not found, going to use invalid keys")

    class DumbObject(object):
        def __getattr__(self, name):
            return 'hunter2'

    keys = DumbObject()

def get_all_instances():
    for mod, cls, i_data in _traverse_lib():
        tag = i_data['tag']
        yield pybikes.get(tag, key=getattr(keys, mod, 'hunter2')), i_data, cls, mod

instances = list(get_all_instances())
tags = [i.tag for i, _, _, _ in instances]
ids = ['%s.%s::%s' % (mod, cls, i.tag) for i, _, cls, mod in instances]

@pytest.mark.parametrize(('instance', 'i_data', 'cls', 'mod'), instances, ids=ids)
class TestInstance:
    def test_tag_unique(self, instance, i_data, cls, mod):
        tag = instance.tag
        err = "tag '%s' is not unique (%s.%s)" % (tag, mod, cls)
        assert tags.count(tag) == 1, err

    def test_fields(self, instance, i_data, cls, mod):
        assert 'tag' in i_data
        assert 'meta' in i_data
        assert re.match(r'^[a-z0-9\-]+$', i_data['tag'])
        for field in ['latitude', 'longitude']:
            assert field in instance.meta
            assert isinstance(instance.meta[field], float)

        for field in ['city', 'country', 'name']:
            assert field in instance.meta

        assert -90 <= instance.meta['latitude'] <= 90
        assert -180 <= instance.meta['longitude'] <= 180

    def test_uses_scraper(self, instance, i_data, cls, mod):
        scraper = pybikes.PyBikesScraper()
        request = Mock
        scraper.request = request
        try:
            instance.update(scraper)
        except Exception:
            pass
        assert request.called

    def test_update(self, instance, i_data, cls, mod):
        scraper = pybikes.PyBikesScraper()
        scraper.requests_timeout = 11
        instance.update(scraper)
        assert len(instance.stations) > 0

        if instance.sync:
            check_for = len(instance.stations)
        else:
            check_for = min(len(instance.stations), 5)

        for i in range(0, check_for):
            station = instance.stations[i]
            station.update(scraper)

            assert isinstance(station.bikes, int)
            assert isinstance(station.latitude, float)
            assert isinstance(station.longitude, float)

            if station.free is not None:
                assert isinstance(station.free, int)
