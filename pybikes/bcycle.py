# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

from pybikes.gbfs import Gbfs, GbfsStation


FEED_URL = "https://gbfs.bcycle.com/{uid}/gbfs.json"

class BCycleStation(GbfsStation):

    def __init__(self, info, * args, ** kwargs):
        super(BCycleStation, self).__init__(info, * args, ** kwargs)

        # similar as velib, ebikes are listed under num_bikes_available_types
        # https://github.com/eskerda/pybikes/blob/master/pybikes/velib.py#L17-L20
        self.extra['has_ebikes'] = True
        self.extra['ebikes'] = int(info['num_bikes_available_types']['electric'])
        self.extra['normal_bikes'] = int(info['num_bikes_available_types']['classic'])


class BCycle(Gbfs):
    station_cls = BCycleStation
    meta = {"system": "BCycle", "company": ["BCycle, LLC"]}

    def __init__(self, tag, meta, uid, * args, ** kwargs):
        # add company if json has additional companies
        if "company" in meta:
            meta["company"] += BCycle.meta["company"]

        feed_url = FEED_URL.format(uid=uid)

        super(BCycle, self).__init__(tag, meta, feed_url, * args, ** kwargs)
