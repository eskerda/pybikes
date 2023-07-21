# Reports

Integration tests can generate a json report file with all extracted data stored
as geojson. Using this json report file, further useful reports can be generated
like a summary of the overall health of the library or a map visualization of
all the information.

```bash
$ make report T_FLAGS+='-n auto -k gbfs'
....
$ ./utils/report.py report/report.json > health.md
$ ./utils/report.py report/report.json --template utils/map.tpl.html > map.html
```

This is the tooling used to generate the summary reports on github [PRs][1]

[1]: https://github.com/eskerda/pybikes/actions/runs/5624574760

The map visualization is very useful to make sense of the extracted data and
detect errors or any inconsistency (wrong lat/lng, test stations showing up)

![map_1](https://github.com/eskerda/pybikes/assets/208952/d0088f1f-9fad-4354-a27d-029c0b32babf)
![map_2](https://github.com/eskerda/pybikes/assets/208952/850c5be2-20ac-4ddf-9e1e-e3c2a724f722)

These are some make steps that are useful shortcuts for generating reports:

```bash
$ make clean
$ make report T_FLAGS+='-n 10 -k bicing'
$ make summary
$ make map
```
