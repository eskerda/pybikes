""" This module is to put any nonsense regarding python versions and import
of compatible methods

It can be used like:
    from pybikes.compat import resources
    ...
"""

try:
    from importlib import resources
    if not hasattr(resources, 'files'):
        raise ImportError()
# Python 3.8
except ImportError:
    import importlib_resources as resources

try:
    from datetime import datetime, timezone
    utcnow = lambda: datetime.now(timezone.utc)
except ImportError:  # python < 3.2
    from datetime import datetime
    utcnow = datetime.utcnow
