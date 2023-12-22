try:
    # python 3
    from unittest.mock import patch, Mock
except ImportError:
    # python 2
    from mock import patch, Mock

import pytest
import requests

from pybikes import BikeShareStation, PyBikesScraper
from pybikes.utils import filter_bounds


def test_filter_bounds():
    """ Tests that filter_bounds utils function correctly filters stations
    out of a given number of bounds. Function must accept multiple lists
    of points to form polygons (4 for a box, oc)."""
    in_bounds = [
        # First bound
        BikeShareStation(latitude=1.1, longitude=1.1),
        BikeShareStation(latitude=2.2, longitude=2.2),
        BikeShareStation(latitude=3.3, longitude=3.3),
        BikeShareStation(latitude=4.4, longitude=4.4),

        # Second bound
        BikeShareStation(latitude=21.0, longitude=21.0),
        BikeShareStation(latitude=22.0, longitude=22.0),
        BikeShareStation(latitude=23.0, longitude=23.0),
        BikeShareStation(latitude=24.0, longitude=24.0),
    ]
    off_bounds = [
        BikeShareStation(latitude=11.1, longitude=11.1),
        BikeShareStation(latitude=12.2, longitude=12.2),
        BikeShareStation(latitude=13.3, longitude=13.3),
        BikeShareStation(latitude=14.4, longitude=14.4),
    ]
    bounds = ([
        [0.0, 0.0],
        [5.0, 0.0],
        [5.0, 5.0],
        [0.0, 5.0]
    ], [
        # This bounding box is a set of two points, NE, SW
        [20.0, 25.0],
        [25.0, 20.0],
    ])
    result = filter_bounds(in_bounds + off_bounds, None, *bounds)

    assert in_bounds == list(result)


def test_filter_bounds_with_key():
    """ Tests that filter_bounds accepts a key parameter """
    in_bounds = [
        # First bound
        {'x': 1.1, 'y': 1.1},
        {'x': 2.2, 'y': 2.2},
        {'x': 3.3, 'y': 3.3},
        {'x': 4.4, 'y': 4.4},
        # Second bound
        {'x': 21.1, 'y': 21.1},
        {'x': 22.2, 'y': 22.2},
        {'x': 23.3, 'y': 23.3},
        {'x': 24.4, 'y': 24.4},
    ]
    off_bounds = [
        {'x': 11.1, 'y': 11.1},
        {'x': 12.2, 'y': 12.2},
        {'x': 13.3, 'y': 13.3},
        {'x': 14.4, 'y': 14.4},
    ]
    bounds = ([
        [0.0, 0.0],
        [5.0, 0.0],
        [5.0, 5.0],
        [0.0, 5.0]
    ], [
        # This bounding box is a set of two points, NE, SW
        [20.0, 25.0],
        [25.0, 20.0],
    ])
    result = filter_bounds(
        in_bounds + off_bounds,
        lambda s: (s['x'], s['y']),
        * bounds
    )

    assert in_bounds == list(result)


class TestPyBikesScraper:

    class FakeSession(Mock):
        response_data = {
            'headers': {},
            'status_code': 200,
            'text': 'hi'
        }

        def request(self, * args, ** kwargs):
            r = Mock(requests.Request, * args, ** kwargs)
            return Mock(requests.Response, request=r, ** self.response_data)

    @pytest.fixture()
    def fake_session(self):
        session = TestPyBikesScraper.FakeSession()
        session.request = Mock(side_effect=session.request)
        with patch('requests.sessions.Session.request', session.request):
            yield session

    def test_default_useragent(self, fake_session):
        scraper = PyBikesScraper()
        scraper.request('https://citybik.es')
        req = scraper.last_request.request
        assert req.headers['User-Agent'] == 'PyBikes'

    def test_base_headers(self, fake_session):
        headers = {
            'Hello-World': 42,
            'Foo': 'Bar',
        }
        scraper = PyBikesScraper(headers=headers)
        scraper.request('https://citybik.es')
        req = scraper.last_request.request

        assert req.headers == headers

    def test_req_headers(self, fake_session):
        headers = {
            'Hello-World': 42,
        }

        req_headers = {
            'Foo': 'Bar',
            'Hello-World': 45,
        }

        scraper = PyBikesScraper(headers=headers)
        scraper.request('https://citybik.es', headers=req_headers)
        req = scraper.last_request.request

        assert req.headers == dict(req.headers, ** req_headers)
        # checks that original headers are unaffected
        assert headers != req_headers

        # next request uses base headers
        scraper.request('https://citybik.es')
        req = scraper.last_request.request
        assert req.headers == headers

    def test_set_cookie(self, fake_session):
        scraper = PyBikesScraper()
        fake_session.response_data['headers']['set-cookie'] = 'Hello'
        scraper.request('https://citybik.es')
        assert scraper.headers['Cookie'] == 'Hello'

    def test_cache_disabled(self, fake_session):
        scraper = PyBikesScraper()
        scraper.request('https://citybik.es')

    def test_uses_cache_if_provided(self, fake_session):
        cache = {}
        scraper = PyBikesScraper(cache)
        scraper.request('https://citybik.es')
        assert 'https://citybik.es' in cache
        assert fake_session.request.called

        fake_session.request.reset_mock()

        scraper.request('https://citybik.es')
        assert not fake_session.request.called

    def test_skip_cache(self, fake_session):
        cache = {}
        scraper = PyBikesScraper(cache)
        scraper.request('https://citybik.es')
        assert 'https://citybik.es' in cache

        fake_session.request.reset_mock()

        scraper.request('https://citybik.es', skip_cache=True)
        assert fake_session.request.called

    def test_disable_cache(self, fake_session):
        cache = {}
        scraper = PyBikesScraper(cache)
        scraper.request('https://citybik.es')
        assert 'https://citybik.es' in cache

        fake_session.request.reset_mock()

        scraper.use_cache = False
        scraper.request('https://citybik.es')
        assert fake_session.request.called

        fake_session.request.reset_mock()

        scraper.use_cache = True
        scraper.request('https://citybik.es')
        assert not fake_session.request.called

    def test_cache_statuses(self, fake_session):
        cache = {}
        scraper = PyBikesScraper(cache)
        fake_session.response_data['status_code'] = 500
        scraper.request('https://citybik.es')

        assert 'https://citybik.es' not in cache

        fake_session.request.reset_mock()
        fake_session.response_data['status_code'] = 200

        scraper.request('https://citybik.es')
        assert 'https://citybik.es' in cache

        scraper.request('https://citybik.es')
        scraper.request('https://citybik.es')
        scraper.request('https://citybik.es')
        scraper.request('https://citybik.es')

        assert fake_session.request.call_count == 1

    def test_forwards_cache_for(self, fake_session):
        scraper = PyBikesScraper()
        mock = Mock()

        with patch('pybikes.contrib.PBCache.set_with_delta', mock):
            scraper.request('https://citybik.es', cache_for=3600)

        response = scraper.last_request

        assert mock.called_with('https://citybik.es', response, 3600)
