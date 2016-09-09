# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the LGPL license, see LICENSE.txt
"""bicicard.py

The Bicicard system (Spain, ITCL), only provides information on the status
of the stations, but not their position (which is provided in a pdf / jpg map,
go figure). The only way to get a consistent feed for that is providing the
location of the stations on a different feed (for instance, a KML feed), and
then map these to the shitty-table-status-page, as in:

    - Map: http://goo.gl/maps/C2xLB (community provided map)
    - KML: http://goo.gl/xGScNY (same map, output as kml)
    - Status: http://www.bicileon.com/estado/EstadoActual.asp

The mapping is done on the description field (on the KML), and the name will
be used as the valid and definitive name. So, for instance:
KML
    Name: Foo's bar awesomest place (fancy name)
    Description: Foo Bar baz
    Coordinates: 1.2, 3.4, 0.0

Status:
    <table> {...}
        <td class="titulo">Fo Bar baz - EN LINIA</td> ◁───────────┬ :)
        {...}                                                     │
        <td width="100" class="lat2" nowrap>{...}</td>            │
        <td width="100" class="lat2" nowrap>ESTADO - (2/10)</td> ◁┘
        <td width="65" align="center" class="ico" nowrap bgcolor="#F0F0F0">
            <img src="no.jpg">
        </td>
        <td width="65" align="center" class="ico" nowrap bgcolor="#E7FE68">
            <img src="si.jpg">
        </td>
        <td width="65" align="center" class="ico" nowrap bgcolor="#F0F0F0">
            <img src="no.jpg">
        </td>
        {...}
        <td width="65" align="center" class="ico" nowrap bgcolor="#E7FE68">
            <img src="si.jpg">
        </td>
    </table>

    This station would have 1 free bike and 9 parking slots (10 total), and
    distributed as P B P P P P P P P B.

    The stations are either EN LÍNEA (online) or FUERA DE LÍNEA (offline)

    Now, we can either count the "si" and "no" imgs, or just get the info
    from the "lat2" td. The first is funnier (in the eye-spoon horror way) and
    the latter makes, I guess, more sense.

We are not going to manually map the stations of all the sharing networks that
use this system, but if the community does it, that's ok (assumedly, this
information one day will be public / maybe we can ask them to make a dump).
"""

import re
from pkg_resources import resource_string

from lxml import etree, html

from pybikes.base import BikeShareSystem, BikeShareStation
from pybikes.utils import PyBikesScraper

__all__ = ['Bicicard']

_kml_ns = {
    'kml': 'http://www.opengis.net/kml/2.2'
}

_xpath_q = "//td[@class='titulo']/text()[contains(.,'%s')]/ancestor::table[1]"\
           "//td[@class='lat2']/text()[contains(.,'ESTADO')]"

_re_bikes_slots = ".*\((?P<bikes>\d+)\/(?P<slots>\d+)\)" #  ESTADO - (1/10)
                                                         #            ↑  ↑
class Bicicard(BikeShareSystem):
    sync = True
    meta = {
        'system': 'Bicicard',
        'company': ['ITCL']
    }

    def __init__(self, tag, kml_file, status_url, meta):
        super(Bicicard, self).__init__(tag, meta)
        self.kml_file = resource_string('pybikes', kml_file)
        self.status_url = status_url

    def update(self, scraper=None):
        if scraper is None:
            scraper = PyBikesScraper()

        status_fuzzle = scraper.request(self.status_url)

        location_dom  = etree.fromstring(self.kml_file)
        status_dom    = html.fromstring(status_fuzzle)

        placemarks = location_dom.xpath("//kml:Placemark",
                                        namespaces = _kml_ns)
        stations = []
        for placemark in placemarks:
            name = placemark.findtext('kml:name', namespaces = _kml_ns)
            name_id = placemark.findtext('kml:description',
                                      namespaces = _kml_ns)
            coor = map(
                float, placemark.findtext('.//kml:coordinates',
                                          namespaces = _kml_ns).
                       split(',')[0:2]
            )

            # Find a status table with the name_id of this station, XPath
            # performance on this query is not really costly so far.
            try:
                (status,) = status_dom.xpath(_xpath_q % name_id)
            except ValueError:
                # Not found.. move along?
                continue

            m = re.search(_re_bikes_slots, status)
            bikes = int(m.group('bikes'))
            slots = int(m.group('slots'))

            station = BikeShareStation()
            station.name       = name
            station.latitude   = coor[1]
            station.longitude  = coor[0]
            station.bikes      = bikes
            station.free       = slots - bikes
            station.extra      = { 'slots': slots }

            stations.append(station)

        self.stations = stations
