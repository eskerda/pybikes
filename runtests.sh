#!/bin/bash
set -e
TRAVIS_BUILD=${TRAVIS_BUILD:-0}
export PYTHONPATH=$PYTHONPATH:.
# It's not a really good idea to test spiders on travis
# limit test to some basic consistency and usage tests
if [ $TRAVIS_BUILD -eq 1 ]; then
    python tests/unittest_pybikes.py TestBikeShareStationInstance
    python tests/unittest_pybikes.py TestBikeShareSystemInstance
    python tests/unittest_pybikes.py TestDataFiles
    python tests/unittest_pybikes.py TestUtils
else
    pip install .
    python tests/unittest_pybikes.py $@
fi
