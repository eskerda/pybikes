import os
import re
import json
from datetime import datetime

import pytest

import pybikes
from pybikes.data import _traverse_lib
from pybikes.utils import keys
from pybikes.compat import mock


def get_all_instances():
    for mod, cls, i_data in _traverse_lib():
        tag = i_data['tag']
        yield pybikes.get(tag, key=getattr(keys, mod) or 'hunter2'), i_data, cls, mod


instances = list(get_all_instances())
tags = [i.tag for i, _, _, _ in instances]
cache = {}
headers = {}

class BaseInstanceTest(object):
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

        assert 'company' in instance.meta

        company = instance.meta['company']
        err = "[company] expected list, found '%s' for %s" % (
            type(company).__name__, company
        )
        assert isinstance(instance.meta['company'], list), err

    def test_uses_scraper(self, instance, i_data, cls, mod):
        scraper = pybikes.PyBikesScraper()
        request = mock.Mock
        scraper.request = request
        try:
            instance.update(scraper)
        except Exception:
            pass
        assert request.called

    @pytest.mark.update
    def test_update(self, instance, i_data, cls, mod, record_property):
        scraper = pybikes.PyBikesScraper(
            # use a simple dict cache for systems that use a single endpoint
            cachedict=cache if instance.unifeed else None,
            # reuse headers per mod
            headers=headers.setdefault(mod, {}),
        )
        scraper.requests_timeout = 11
        instance.update(scraper)
        assert len(instance.stations) > 0

        if instance.sync:
            check_for = len(instance.stations)
        else:
            check_for = min(len(instance.stations), 5)

        for i in range(0, check_for):
            station = instance.stations[i]

            if not instance.sync:
                station.update(scraper)

            assert isinstance(station.bikes, int)
            assert isinstance(station.latitude, float)
            assert isinstance(station.longitude, float)
            assert isinstance(station.timestamp, datetime)

            if station.free is not None:
                assert isinstance(station.free, int)

        # FIXME: there's some serialization issue with pytest-xdist and some
        # of the data (ex: girocleta). Encoding and decoding it again fixes it
        record_property('geojson', json.loads(json.dumps(instance.to_geojson())))


# XXX meh
classes = {
    cls: [x for x in instances if x[2] == cls]
        for cls in set((cls for _, _, cls, _ in instances))
}

# even if pytest does not like it, generate test classes on runtime, so
# instance tests are grouped by their class

def get_test_cls(cls):
    cls_instances = list(classes[cls])
    ids = ['%s.%s::%s' % (mod, cls, i['tag']) for _, i, cls, mod in cls_instances]

    @pytest.mark.parametrize(('instance', 'i_data', 'cls', 'mod'), cls_instances, ids=ids)
    class TestWrap(BaseInstanceTest):
        pass

    name = 'Test%s' % cls
    return type(str(name), (TestWrap,), {})


for cls in sorted(classes):
    test_cls = get_test_cls(cls)
    globals()[test_cls.__name__] = test_cls
