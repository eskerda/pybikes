# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes.gbfs import Gbfs
from pybikes.compat import resources


prefectures = resources.files('pybikes')/'geojson/japan_prefectures.json'
geojson = json.loads(prefectures.read_bytes())


class HelloCycling(Gbfs):
    unifeed = True

    meta = {
        "company": ["OpenStreet Corp."],
        "license": {
            "name": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
            "url": "https://creativecommons.org/licenses/by/4.0/",
        },
        "source": "https://ckan.odpt.org/dataset/c_bikeshare_gbfs-openstreet",
    }

    def __init__(self, tag, meta, uid, bbox=None):
        feed_url = "https://api-public.odpt.org/api/v4/gbfs/hellocycling/gbfs.json"

        bbox = list(
            filter(lambda d: d["properties"]["id"] == uid, geojson["features"])
        )[0]["geometry"]

        super(HelloCycling, self).__init__(tag, meta, feed_url, bbox=bbox)
