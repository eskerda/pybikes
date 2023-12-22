# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

from pybikes.gbfs import Gbfs


FEED_URL = "https://gbfs.bcycle.com/{uid}/gbfs.json"


class BCycle(Gbfs):
    meta = {"system": "BCycle", "company": ["BCycle, LLC"]}

    def __init__(self, tag, meta, uid, bbox=None):
        # add company if json has additional companies
        if "company" in meta:
            meta["company"] += BCycle.meta["company"]

        feed_url = FEED_URL.format(uid=uid)

        super(BCycle, self).__init__(tag, meta, feed_url, bbox=bbox)
