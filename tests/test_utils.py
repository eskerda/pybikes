import json
from pkg_resources import resource_string

import pytest

from pybikes import BikeShareStation
from pybikes.utils import filter_bounds

barcelona = [
    BikeShareStation(latitude=41.38530363280023, longitude=2.1537750659833534),
    BikeShareStation(latitude=41.38670644238084, longitude=2.14627128),
]

girona = [
    BikeShareStation(latitude=41.97290243618622, longitude=2.812822876238897),
]

mordor = [
    BikeShareStation(latitude=-100, longitude=3000),
    BikeShareStation(latitude=0, longitude=0),
]

shape = json.loads(resource_string('tests.fixtures', 'shape.json'))

filter_bounds_cases = [
    (
        "A bbox filter of barcelona displays only stations in Barcelona",
        barcelona + girona + mordor,
        barcelona,
        None,
        [[41.429655489542995, 2.265798843028506], [41.324098007178094, 2.060483133624132]]
    ),
    (
        "A geojson shape filter displays only stations within the filter",
        barcelona + girona + mordor,
        barcelona + girona,
        None,
        shape
    ),
    (
        "A bbox filter of points using a getter display only points within bbox",
        [
            {'lat': 41.3853036328, 'lng': 2.1537750659833534},
            {'lat': 31.3853036328, 'lng': 1.1537750659833534},
        ],
        [
            {'lat': 41.3853036328, 'lng': 2.1537750659833534},
        ],
        lambda thing: (thing['lat'], thing['lng']),
        [[41.429655489542995, 2.265798843028506], [41.324098007178094, 2.060483133624132]],
    ),
    (
        "A shape filter of points using a getter display only points within bbox",
        [
            {'lat': 41.3853036328, 'lng': 2.1537750659833534},
            {'lat': 31.3853036328, 'lng': 1.1537750659833534},
        ],
        [
            {'lat': 41.3853036328, 'lng': 2.1537750659833534},
        ],
        lambda thing: (thing['lat'], thing['lng']),
        shape
    ),
    (
        "A bbox filter of pairs display only points within bbox",
        [
            (41.3853036328, 2.1537750659833534),
            (31.3853036328, 1.1537750659833534),
        ],
        [
            (41.3853036328, 2.1537750659833534),
        ],
        None,
        [[41.429655489542995, 2.265798843028506], [41.324098007178094, 2.060483133624132]],
    ),
    (
        "A shape filter of pairs display only points within bbox",
        [
            (41.3853036328, 2.1537750659833534),
            (31.3853036328, 1.1537750659833534),
        ],
        [
            (41.3853036328, 2.1537750659833534),
        ],
        None,
        shape
    ),
]

@pytest.mark.parametrize("msg, data, expected, getter, bounds", filter_bounds_cases)
def test_filter_bounds(msg, data, expected, getter, bounds):
    assert expected == list(filter_bounds(data, getter, bounds)), msg
