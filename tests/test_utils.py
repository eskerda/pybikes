from pybikes import BikeShareStation
from pybikes.utils import filter_bounds

def test_filter_bounds():
    """ Tests that filter_bounds utils function correctly filters stations
    out of a given number of bounds. Function must accept multiple lists
    of points to form polygons (4 for a box, oc)."""
    in_bounds = [
        # First bound
        BikeShareStation(latitude=1.1, longitude=1.1),
        BikeShareStation(latitude=2.2, longitude=2.2),
        BikeShareStation(latitude=3.3, longitude=3.3),
        BikeShareStation(latitude=4.4, longitude=4.4),

        # Second bound
        BikeShareStation(latitude=21.0, longitude=21.0),
        BikeShareStation(latitude=22.0, longitude=22.0),
        BikeShareStation(latitude=23.0, longitude=23.0),
        BikeShareStation(latitude=24.0, longitude=24.0),
    ]
    off_bounds = [
        BikeShareStation(latitude=11.1, longitude=11.1),
        BikeShareStation(latitude=12.2, longitude=12.2),
        BikeShareStation(latitude=13.3, longitude=13.3),
        BikeShareStation(latitude=14.4, longitude=14.4),
    ]
    bounds = ([
        [0.0, 0.0],
        [5.0, 0.0],
        [5.0, 5.0],
        [0.0, 5.0]
    ], [
        # This bounding box is a set of two points, NE, SW
        [20.0, 25.0],
        [25.0, 20.0],
    ])
    result = filter_bounds(in_bounds + off_bounds, None, *bounds)

    assert in_bounds == list(result)


def test_filter_bounds_with_key():
    """ Tests that filter_bounds accepts a key parameter """
    in_bounds = [
        # First bound
        {'x': 1.1, 'y': 1.1},
        {'x': 2.2, 'y': 2.2},
        {'x': 3.3, 'y': 3.3},
        {'x': 4.4, 'y': 4.4},
        # Second bound
        {'x': 21.1, 'y': 21.1},
        {'x': 22.2, 'y': 22.2},
        {'x': 23.3, 'y': 23.3},
        {'x': 24.4, 'y': 24.4},
    ]
    off_bounds = [
        {'x': 11.1, 'y': 11.1},
        {'x': 12.2, 'y': 12.2},
        {'x': 13.3, 'y': 13.3},
        {'x': 14.4, 'y': 14.4},
    ]
    bounds = ([
        [0.0, 0.0],
        [5.0, 0.0],
        [5.0, 5.0],
        [0.0, 5.0]
    ], [
        # This bounding box is a set of two points, NE, SW
        [20.0, 25.0],
        [25.0, 20.0],
    ])
    result = filter_bounds(
        in_bounds + off_bounds,
        lambda s: (s['x'], s['y']),
        * bounds
    )

    assert in_bounds == list(result)
