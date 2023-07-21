T_FLAGS =

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

test: install
	pytest tests -m 'not update' $(T_FLAGS)

test-update: install
	pytest tests -m update $(T_FLAGS)

lint:
	flake8 pybikes tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 pybikes tests --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

report/report.json:
	pytest tests -m update --json-report --json-report-file=report/report.json $(T_FLAGS)

report: report/report.json

summary: report/report.json
	./utils/report.py report/report.json

map: report/report.json
	./utils/report.py report/report.json --template utils/map.tpl.html

.PHONY: install test test-update lint report summary map
