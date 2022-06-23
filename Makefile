.PHONY: test cov bench
default_target: cov
REPEAT=5
clean:
	@echo "removing existing builds ..."
	@rm -rf dist/ build/ *egg*info
test:
	@pytest
cov:
	@coverage run -m pytest && coverage html
bench:
	richbench --profile --repeat ${REPEAT} tests/benchmarks
build: clean
	python setup.py sdist bdist_wheel
req:
	@pipenv requirements | grep -v typing > requirements.txt
	@pipenv requirements --dev | grep -v typing | grep -v coverage > dev_requirements.txt
	@echo "coverage" >> dev_requirements.txt