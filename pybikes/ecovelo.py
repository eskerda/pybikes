# -*- coding: utf-8 -*-
# Copyright (C) 2021, Altonss https://github.com/Altonss
# Distributed under the AGPL license, see LICENSE.txt

from pybikes.gbfs import Gbfs

class Ecovelo(Gbfs):

    meta = {
        'system': 'Ecovelo',
        'company': ['Ecovelo'],
    }

    BASE_URL = "https://api.gbfs.v1.ecovelo.mobi/gbfs/{dataset}"

    def __init__(self, tag, dataset, meta):
        feed_url = Ecovelo.BASE_URL.format(dataset=dataset)
        super(Ecovelo, self).__init__(tag, meta, feed_url)
