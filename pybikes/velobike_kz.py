import json

from lxml import html

from pybikes import BikeShareSystem, BikeShareStation, PyBikesScraper


def maybe_number(thing, default=0):
    try:
        return int(thing)
    except ValueError:
        return default


class VelobikeKZ(BikeShareSystem):

    meta = {
        'company': ['CTS']
    }

    def __init__(self, tag, feed_url, meta):
        super().__init__(tag, meta)
        self.feed_url = feed_url

    def parse_row(self, row):
        latitude = float(row.attrib['data-latitude'])
        longitude = float(row.attrib['data-longitude'])

        name = row.xpath('.//td[contains(@class, "name")]')[0].text.strip()

        bikes = maybe_number(row.xpath('.//td[contains(@class, "avl-bikes")]')[0].text.strip())
        free = maybe_number(row.xpath('.//td[contains(@class, "free-slots")]')[0].text.strip())

        online = len(row.xpath('.//td[span]')) == 0

        extra = {
            'online': online,
            'slots': maybe_number(row.attrib['data-total-slots']),
            'address': row.xpath('.//td[contains(@class, "address")]')[0].text.strip(),
            'uid': row.xpath('.//th[contains(@class, "code")]')[0].text.strip(),
        }

        return BikeShareStation(name, latitude, longitude, bikes, free, extra)

    def update(self, scraper=None):
        scraper = scraper or PyBikesScraper()

        fuzzle = scraper.request(self.feed_url)
        tree = html.fromstring(fuzzle)
        rows = tree.xpath("""
            //table[contains(@class, 'table-stations')]
                //tbody//tr
        """)
        self.stations = list(map(lambda r: self.parse_row(r), rows))
