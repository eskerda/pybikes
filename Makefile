T_FLAGS =
R_FILE ?= report.json

.PHONY: install
install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

.PHONY: test
test: install
	pytest tests -m 'not update and not changes' $(T_FLAGS)

.PHONY: test-update
test-update: install
	pytest tests -m update $(T_FLAGS)

.PHONY: test-changes
test-changes: install
	pytest tests -m changes $(T_FLAGS)

.PHONY: lint
lint:
	flake8 pybikes tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 pybikes tests --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

report/$(R_FILE):
	pytest tests -m update $(T_FLAGS) --json-report --json-report-file=report/$(R_FILE)

.PHONY: report
report: report/$(R_FILE)

.PHONY: report!
report!: clean report

.PHONY: summary
summary: report/$(R_FILE)
	@./utils/report.py report/$(R_FILE)

.PHONY: map
map: report/$(R_FILE)
	@./utils/report.py report/$(R_FILE) --template utils/map.tpl.html > report/map.html
	@open report/map.html || xdg-open report/map.html

.PHONY: map!
map!: clean map

.PHONY: github-summary
github-summary: report/$(R_FILE)
	@./utils/report.py report/$(R_FILE) --template utils/github-summary.tpl.md

.PHONY: clean
clean: clean-report

.PHONY: clean-report
clean-report:
	rm -rf report/
