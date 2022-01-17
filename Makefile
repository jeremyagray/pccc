#***********************************************************************
#
# pccc, the Python Conventional Commit Checker.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2020-2022 Jeremy A Gray <gray@flyquackswim.com>.
#
#***********************************************************************

python-modules = pccc tests
python-files =

.PHONY : test-all
test-all:
	pytest -vv --cov pccc --cov tests --cov-report term --cov-report html

.PHONY : build
build :
	cd docs && make html
	pip install -q build
	python -m build

.PHONY : clean
clean :
	rm -rf build
	rm -rf dist
	rm -rf pccc.egg-info
	cd docs && make clean

.PHONY : dist
dist : clean build

.PHONY : commit
commit :
	pre-commit run --all-files

.PHONY : lint
lint :
	flake8 --exit-zero $(python-modules) $(python-files)
	isort --check $(python-modules) $(python-files) || exit 0
	black --check $(python-modules) $(python-files)

.PHONY : lint-fix
lint-fix :
	isort $(python-modules) $(python-files)
	black $(python-modules) $(python-files)

.PHONY : pip
pip :
	pip install -r requirements.txt

.PHONY : test
test :
	pytest

.PHONY : upload
upload :
	python3 -m twine upload --verbose dist/*

.PHONY : upload-test
upload-test :
	python3 -m twine upload --verbose --repository testpypi dist/*

requirements.txt: poetry.lock
	./freeze.sh > $(@)
