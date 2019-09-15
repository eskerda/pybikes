# -*- coding: utf-8 -*-

try:
    # Python 2
    from urlparse import urljoin
except ImportError:
    # Python 3
    from urllib.parse import urljoin

from pybikes.gbfs import Gbfs
from pybikes.utils import PyBikesScraper


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

    @staticmethod
    def authorize(scraper, key):
        request = scraper.request

        def _request(*args, **kwargs):
            params = kwargs.get('params', {})
            params.update(key)
            kwargs['params'] = params
            return request(*args, **kwargs)

        scraper.request = _request

    def update(self, scraper=None):
        # Patch default scraper request method
        scraper = scraper or PyBikesScraper()
        EcobiciBA.authorize(scraper, self.key)
        super(EcobiciBA, self).update(scraper)
