from pybikes import PyBikesScraper
from pybikes.utils import Bounded
from pybikes.otp import OTP


FEED_URL = "https://api.digitransit.fi/routing/v2/finland/gtfs/v1"


class Digitransit(Bounded, OTP):
    authed = True
    unifeed = True

    meta = {}

    def __init__(self, tag, meta, key, bbox=None):
        super().__init__(tag, meta, feed_url=FEED_URL, bounds=bbox)
        self.key = key

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        scraper.headers.update({"digitransit-subscription-key": self.key})
        super().update(scraper)
