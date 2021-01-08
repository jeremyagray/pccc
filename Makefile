#***********************************************************************
#
# Makefile - chore makefile for pccc
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# pccc, the Python Conventional Commit Checker.
# Copyright (C) 2020-2021 Jeremy A Gray <jeremy.a.gray@gmail.com>.
#
#***********************************************************************

.PHONY : build clean dist commit lint pip upload upload-test test test-all

test-all:
	pytest -vv --black --flake8 --pydocstyle --cov pccc --cov-report term --cov-report html

build :
	cd docs && make html
	pip install -q build
	python -m build

clean :
	rm -rf build
	rm -rf dist
	rm -rf pccc.egg-info
	cd docs && make clean

dist : clean build

commit :
	pre-commit run --all-files

lint :
	pytest --lint-only --black --flake8 --pydocstyle

pip :
	pip install -r requirements.txt

test:
	pytest --cov pccc --cov-report term

upload:
	python3 -m twine upload --verbose dist/*

upload-test:
	python3 -m twine upload --verbose --repository testpypi dist/*
