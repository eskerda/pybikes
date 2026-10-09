import json
from datetime import timedelta

import pytest

from pybikes.compat import utcnow
from pybikes.gira import GiraSystem


def feature(uid, estado, update_date, lng=-9.149334, lat=38.724954):
    return {
        'type': 'Feature',
        'geometry': {'type': 'MultiPoint', 'coordinates': [[lng, lat]]},
        'properties': {
            'id_expl': uid,
            'desig_comercial': '%s - Some station' % uid,
            'num_bicicletas': 5,
            'num_docas': 20,
            'estado': estado,
            'update_date': update_date,
        },
    }


def iso(dt):
    # same format as EMEL's feed: 2026-10-09T22:15:01Z
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


class FakeScraper:
    def __init__(self, features):
        self.features = features

    def request(self, url, *args, **kwargs):
        return json.dumps({'type': 'FeatureCollection', 'features': self.features})


def update(features):
    gira = GiraSystem('gira', 'https://example.com/wfs', {'name': 'Gira'})
    gira.update(FakeScraper(features))
    return {s.extra['uid']: s for s in gira.stations}


@pytest.fixture()
def now():
    return utcnow()


def test_all_repair_is_ignored(now):
    # EMEL reports estado='repair' for every station: use freshness instead
    stations = update([
        feature('1', 'repair', iso(now - timedelta(minutes=3))),
        feature('2', 'repair', iso(now - timedelta(days=77))),
    ])
    assert stations['1'].extra['online'] is True
    assert stations['2'].extra['online'] is False
    assert stations['1'].extra['status'] == 'repair'


def test_status_is_used_when_meaningful(now):
    fresh = iso(now - timedelta(minutes=3))
    stations = update([
        feature('1', 'active', fresh),
        feature('2', 'repair', fresh),
        feature('3', 'active', iso(now - timedelta(days=2))),
    ])
    assert stations['1'].extra['online'] is True
    assert stations['2'].extra['online'] is False
    assert stations['3'].extra['online'] is False


def test_last_updated(now):
    stations = update([feature('1', 'repair', '2026-10-09T22:15:01Z')])
    assert stations['1'].extra['last_updated'] == '2026-10-09T22:15:01+00:00'


@pytest.mark.parametrize('update_date', [None, '', 'not a date'])
def test_missing_or_bad_update_date(update_date):
    stations = update([feature('1', 'repair', update_date)])
    assert stations['1'].extra['online'] is True
    assert 'last_updated' not in stations['1'].extra
