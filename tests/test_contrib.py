import pytest

try:
    # python 3
    from unittest.mock import patch
except ImportError:
    # python 2
    from mock import patch


from pybikes import BikeShareSystem
from pybikes.contrib import TSTCache, PBCache


# Acts as time module, with some extra wizz
class FakeTime:

    the_time = 0.0

    def time(self):
        return self.the_time

    def travel(self, delta):
        self.the_time += delta


class TestTSTCache:

    @pytest.fixture()
    def cache(self):
        self._store = {}
        return TSTCache(self._store, 60)

    @pytest.fixture()
    def store(self, cache):
        return self._store

    @pytest.fixture()
    def time_machine(self):
        it = FakeTime()
        with patch('time.time', it.time):
            yield it

    def test_set_get(self, cache, time_machine):
        # time is 0.0
        cache['foo'] = 'bar'
        assert cache['foo'] == 'bar'

        # time is 30.0
        time_machine.travel(30)
        assert cache['foo'] == 'bar'
        cache['bar'] = 'baz'
        assert cache['bar'] == 'baz'

        # time is 70.0
        time_machine.travel(40)
        assert 'foo' not in cache
        with pytest.raises(KeyError):
            cache['foo']

        assert cache['bar'] == 'baz'

        # time is 100.0
        time_machine.travel(30)
        assert 'bar' not in cache
        with pytest.raises(KeyError):
            cache['bar']



class FooBikeShare(BikeShareSystem):
    domain = 'foo.com'

    def update(self, scraper):
        scraper.request('https://%s/%s' % (self.domain, self.tag))


class BarBikeShare(FooBikeShare):
    domain = 'bar.com'

    def auth(self, scraper):
        scraper.request('https://%s/auth' % (self.domain))

    def update(self, scraper):
        self.auth(scraper)
        scraper.request('https://%s/%s' % (self.domain, self.tag))


class BazBikeShare(FooBikeShare):
    domain = 'baz.com'


class FuzzBikeShare(FooBikeShare):
    domain = 'fuzz.com'


class TestPBCache(TestTSTCache):
    @pytest.fixture()
    def cache(self, deltas):
        self._store = {}
        return PBCache(self._store, 60, deltas=deltas)

    @pytest.fixture()
    def deltas(self):
        return [
            {'foobikeshare::foo-corp-haven::.*': 10},
            {'foobikeshare::foo-end-city::.*': 20},
            {'foobikeshare::.*': 30},
            {'barbikeshare::.*::auth::.*': 100},
            {'barbikeshare::bar-mad-isle::update::.*': 40},
            {'barbikeshare::bar-neo-troy::update::.*': 60},
            {'.*::.*::.*::https://baz.com': 120},
        ]

    @pytest.fixture()
    def instances(self):
        return [
            FooBikeShare('foo-corp-haven', meta={'name': 'Foo Corp Haven', 'system': 'foo'}),
            FooBikeShare('foo-end-city', meta={'name': 'Foo End City', 'system': 'foo'}),
            FooBikeShare('foo-devil-hold', meta={'name': 'Foo Devil Hold', 'system': 'foo'}),

            BarBikeShare('bar-mad-isle', meta={'name': 'Bar Mad Isle', 'system': 'bar'}),
            BarBikeShare('bar-neo-troy', meta={'name': 'Bar Neo Troy', 'system': 'bar'}),

            BazBikeShare('baz-greed-city', meta={'name': 'Baz Greed City', 'system': 'baz'}),
            BazBikeShare('baz-droid-town', meta={'name': 'Baz Droid Town', 'system': 'baz'}),

            FuzzBikeShare('fuzz-neo-titania', meta={'name': 'Fuzz Neo Titania', 'system': 'fuzz'}),
            FuzzBikeShare('fuzz-chaos-trail', meta={'name': 'Fuzz Chaos Trail', 'system': 'fuzz'}),
        ]

    @pytest.fixture()
    def instance_map(self, instances):
        return {i.tag: i for i in instances}

    @pytest.fixture()
    def scraper(self, cache):
        class Scraper:
            hits = 0
            miss = 0

            def request(self, url, * args, ** kwargs):
                if url in cache:
                    self.hits += 1
                    return cache[url]

                self.miss += 1

                data = 'Some request data'
                cache[url] = data
                return data

            def reset(self):
                self.hits = 0
                self.miss = 0

        return Scraper()

    def test_deltas(self, cache, scraper, instances, time_machine):
        # time is 0
        [i.update(scraper) for i in instances]
        assert scraper.hits == 1
        assert scraper.miss == 10

        scraper.reset()
        [i.update(scraper) for i in instances]
        assert scraper.hits == 11
        assert scraper.miss == 0

        scraper.reset()
        time_machine.travel(1000)

        [i.update(scraper) for i in instances]
        assert scraper.hits == 1
        assert scraper.miss == 10

    def test_tag_delta(self, cache, scraper, instances, time_machine):
        # time is 0
        [i.update(scraper) for i in instances if 'foo' in i.tag]
        assert scraper.miss == 3

        time_machine.travel(15)
        scraper.reset()

        [i.update(scraper) for i in instances if 'foo' in i.tag]
        assert scraper.hits == 2
        assert scraper.miss == 1

        time_machine.travel(15)
        scraper.reset()

        [i.update(scraper) for i in instances if 'foo' in i.tag]
        assert scraper.hits == 1
        assert scraper.miss == 2

    def test_method_delta(self, cache, scraper, instances, time_machine):
        # time is 0
        [i.update(scraper) for i in instances if 'bar' in i.tag]
        assert scraper.miss == 3
        assert scraper.hits == 1

        time_machine.travel(90)
        scraper.reset()

        [i.update(scraper) for i in instances if 'bar' in i.tag]
        assert scraper.miss == 2
        assert scraper.hits == 2

    def test_url_delta(self, cache, scraper, instances, time_machine):
        # time is 0
        [i.update(scraper) for i in instances if 'baz' in i.tag]
        assert scraper.miss == 2
        assert scraper.hits == 0

        time_machine.travel(100)
        scraper.reset()

        [i.update(scraper) for i in instances if 'baz' in i.tag]
        assert scraper.miss == 0
        assert scraper.hits == 2

        time_machine.travel(100)
        scraper.reset()

        [i.update(scraper) for i in instances if 'baz' in i.tag]
        assert scraper.miss == 2
        assert scraper.hits == 0

    def test_default_delta(self, cache, scraper, instances, time_machine):
        # time is 0
        [i.update(scraper) for i in instances if 'fuzz' in i.tag]
        assert scraper.miss == 2
        assert scraper.hits == 0

        time_machine.travel(30)
        scraper.reset()

        [i.update(scraper) for i in instances if 'fuzz' in i.tag]
        assert scraper.miss == 0
        assert scraper.hits == 2

        time_machine.travel(60)
        scraper.reset()

        [i.update(scraper) for i in instances if 'fuzz' in i.tag]
        assert scraper.miss == 2
        assert scraper.hits == 0

    def test_with_delta(self, cache, scraper, time_machine):
        cache.set_with_delta('foo', 'Foobar', 30)
        assert cache['foo'] == 'Foobar'

        time_machine.travel(50)

        with pytest.raises(KeyError):
            cache['foo']

    def test_delta_zero(self, cache):
        assert cache.__get_delta__('', {'delta': 0}) == 0

    def test_default_delta_if_None(self, cache):
        assert cache.__get_delta__('', {'delta': None}) == cache.delta
