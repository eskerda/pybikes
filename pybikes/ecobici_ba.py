# -*- coding: utf-8 -*-

from urlparse import urljoin

from pybikes.gbfs import Gbfs
from pybikes.utils import PyBikesScraper


class AuthScraper(PyBikesScraper):
    def __init__(self, key, *args, **kwargs):
        self.key = key
        super(AuthScraper, self).__init__(*args, **kwargs)

    def request(self, *args, **kwargs):
        params = kwargs.get('params', {})
        params['client_id'] = self.key.get('client_id', None)
        params['client_secret'] = self.key.get('client_secret', None)
        kwargs['params'] = params
        return super(AuthScraper, self).request(*args, **kwargs)


class EcobiciBA(Gbfs):
    authed = True

    meta = {
        'system': 'BA Ecobici',
        'company': ['Buenos Aires Ciudad'],
        'license': {
            'name': 'Open Data Commons Open Database License 1.0 (ODbL)',
            'url': 'https://opendatacommons.org/licenses/odbl/',
        },
        'source': 'https://www.buenosaires.gob.ar/desarrollourbano/transporte/apitransporte',
    }

    def __init__(self, tag, meta, feed_url, key):
        super(EcobiciBA, self).__init__(tag, meta, feed_url)
        self.key = key

    @property
    def default_feeds(self):
        url = self.feed_url
        return {
            "station_information": urljoin(url, 'stationInformation'),
            "station_status": urljoin(url, 'stationStatus'),
        }

    def update(self, scraper=None):
        scraper = scraper or AuthScraper(self.key)
        super(EcobiciBA, self).update(scraper)
