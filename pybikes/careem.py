# -*- coding: utf-8 -*-
# Copyright (C) 2023, Martín González Gómez <m@martingonzalez.net>
# Distributed under the AGPL license, see LICENSE.txt

from pybikes.gbfs import Gbfs


class Careem(Gbfs):
    unifeed = True

    meta = {"company": ["Careem"]}

    def __init__(self, tag, meta, bbox=None):
        feed_url = "https://dubai.publicbikesystem.net/customer/gbfs/v2/en/gbfs.json"
        super(Careem, self).__init__(tag, meta, feed_url, bbox=bbox)
