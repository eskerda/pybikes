export PYTHONPATH=$PYTHONPATH:.
python2 setup.py install
python2 tests/unittest_pybikes.py $@
