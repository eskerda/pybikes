from pybikes import PyBikesScraper
from pybikes.gbfs import Gbfs


# See https://github.com/SFOE/sharedmobility

class SharedMobility(Gbfs):

    authed = True

    meta = {
        "license": {
            "name": "Open Use",
            "url": "https://opendata.swiss/en/dataset/standorte-und-verfugbarkeit-von-shared-mobility-angeboten",
        },
        "source": "https://github.com/SFOE/sharedmobility/blob/main/Access%20the%20data.md",
    }

    def __init__(self, key, * args, ** kwargs):
        self.auth = key
        super(SharedMobility, self).__init__(* args, ** kwargs)

    @property
    def auth_headers(self):
        # According to https://github.com/SFOE/sharedmobility/blob/main/Access%20the%20data.md
        # This is an email address so they can contact back
        return {
            'Authorization': self.auth,
        }

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()
        scraper.headers.update(self.auth_headers)
        super(SharedMobility, self).update(scraper)
