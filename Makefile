LINT_FILES=perra wizard.py scripts tests

test:
	coverage run --source=./perra,./perra/web -m pytest tests
	coverage report -m
	coverage html

rerun-tests:
	pytest --lf -vv

lint:
	@echo 'syntax errors or undefined names'
	flake8 --count --select=E9,F63,F7,F82 --show-source --statistics ${LINT_FILES}

	@echo 'warning'
	flake8 --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --ignore=E731,W503,E501 ${LINT_FILES}

	@echo 'mypy'
	mypy --check-untyped-defs ${LINT_FILES}

speed:
	time python3 -m perra --version
	python3 -c "import timeit; t = timeit.Timer('import perra'); print(t.timeit(number = 1000000))"
	python3 -X importtime -c "import perra" 2> perra-import.log
	python3 -m tuna perra-import.log

format:
	@echo 'black'
	black --skip-string-normalization ${LINT_FILES}

pull:
	git stash
	git checkout main
	git pull origin main
	git stash pop

clean:
	rm -rf reports htmlcov dist build

install:
	pip3 install .
