override T_FLAGS += -v
install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

test: test-base test-instances test-update-instances

test-base:
	pytest tests -k 'not test_instances' $(T_FLAGS)

test-instances:
	pytest tests -k 'test_instances and not test_update' $(T_FLAGS)

test-update-instances:
	pytest tests -k 'test_instances and test_update' $(T_FLAGS)

lint:
	flake8 pybikes tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 pybikes tests --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
