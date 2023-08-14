T_FLAGS =

.PHONY: install
install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

.PHONY: test
test: install
	pytest tests -m 'not update' $(T_FLAGS)

.PHONY: test-update
test-update: install
	pytest tests -m update $(T_FLAGS)

.PHONY: lint
lint:
	flake8 pybikes tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 pybikes tests --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

report/report.json:
	pytest tests -m update --json-report --json-report-file=report/report.json $(T_FLAGS)

.PHONY: report
report: report/report.json

.PHONY: summary
summary: report/report.json
	@./utils/report.py report/report.json

.PHONY: map
map: report/report.json
	@./utils/report.py report/report.json --template utils/map.tpl.html > report/map.html
	open report/map.html

.PHONY: map!
map!: clean map

.PHONY: github-summary
github-summary: report/report.json
	@./utils/report.py report/report.json --template utils/github-summary.tpl.md

.PHONY: clean
clean: clean-report

.PHONY: clean-report
clean-report:
	rm -rf report/
