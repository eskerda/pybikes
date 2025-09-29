from pybikes import PyBikesScraper
from pybikes.utils import Bounded
from pybikes.otp import OTP


DEFAULT_FEED_URL = "https://api.digitransit.fi/routing/v2/finland/gtfs/v1"


class Digitransit(Bounded, OTP):
    authed = True
    unifeed = True

    meta = {
        "source": "https://digitransit.fi",
        "license": {
            "name": "Creative Commons name 4.0 (CC BY)",
            "url": "https://digitransit.fi/en/developers/apis/7-terms-of-use/#3-digitransit-data",
        }
    }

    def __init__(self, tag, meta, key, feed_url=DEFAULT_FEED_URL, bbox=None):
        super().__init__(tag, meta, feed_url=feed_url, bounds=bbox)
        self.key = key

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        scraper.headers.update({"digitransit-subscription-key": self.key})
        super().update(scraper)
