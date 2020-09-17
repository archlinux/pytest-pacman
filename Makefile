PYTHON?=python
FLAKE8?=flake8
PYTEST?=py.test
PYTEST_OPTIONS+=-s
PYTEST_INPUT?=test
PYTEST_COVERAGE_OPTIONS+=--cov-report=term-missing --cov-report=html:test/coverage --cov=pytest_pacman
EXT_COVERAGE_DIR=test/ext-coverage

.PHONY: test lint

test:
	PYTHONPATH=. ${PYTEST} ${PYTEST_INPUT} ${PYTEST_OPTIONS} ${PYTEST_COVERAGE_OPTIONS}

lint:
	$(FLAKE8) pytest_pacman
