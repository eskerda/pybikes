# -*- coding: utf-8 -*-
# Copyright (C) 2024, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

import json

from pybikes.gbfs import Gbfs
from pybikes.compat import resources


prefectures = resources.files('pybikes')/'geojson/japan_prefectures.json'
geojson = json.loads(prefectures.read_bytes())


class Docomo(Gbfs):

    unifeed = True

    meta = {
        "company": [
            "DOCOMO BIKE SHARE, INC."
        ],
        "license": {
            "name": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
            "url": "https://creativecommons.org/licenses/by/4.0/"
        },
        "source": "https://ckan.odpt.org/en/dataset/c_bikeshare_gbfs-d-nationwide-bikeshare"
    }

    def __init__(self, tag, meta, uid, bbox=None):
        feed_url = "https://api-public.odpt.org/api/v4/gbfs/docomo-cycle/gbfs.json"

        bbox = list(
            filter(lambda d: d["properties"]["id"] == uid, geojson["features"])
        )[0]["geometry"]

        super(Docomo, self).__init__(tag, meta, feed_url, bbox=bbox)
