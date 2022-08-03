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
