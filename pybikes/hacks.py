# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt


hack_table = {
    'cristolib': ['cristolib'],
    'le-velo': ['levelo']
}

class cristolib(object):
    def markers(self, markers):
        return [marker for marker in markers if int(marker.attrib['number']) < 30]

class levelo(object):
    def markers(self, markers):
        return [marker for marker in markers if int(marker.attrib['number']) != 602]
