""" This module is to put any nonsense regarding python versions and import
of compatible methods

It can be used like:
    from pybikes.compat import urljoin
    ...
"""

try:
    from importlib import resources
    if not hasattr(resources, 'files'):
        raise ImportError()
# Python 2.7, 3.8
except ImportError:
    import importlib_resources as resources

try:
    # Python 2
    from urlparse import urljoin
except ImportError:
    # Python 3
    from urllib.parse import urljoin

try:
    # Python 2
    from itertools import imap as map
except ImportError:
    # Python 3
    map = map

try:
    # Python 2
    from urllib import unquote_plus
except ImportError:
    # Python 3
    from urllib.parse import unquote_plus

try:
    # python 3
    import unittest.mock as mock
except ImportError:
    # python 2
    import mock


try:
    from urlparse import urlparse
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import urlparse
    from urllib.parse import parse_qs
