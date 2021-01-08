#***********************************************************************
#
# Makefile - chore makefile for pccc
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# pccc, the Python Conventional Commit Checker.
# Copyright (C) 2020-2021 Jeremy A Gray <jeremy.a.gray@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#***********************************************************************

.PHONY : build clean commit lint pip upload upload-test test test-all

test-all:
	pytest -vv --black --flake8 --pydocstyle --cov pccc --cov-report term --cov-report html

build :
	pip install -q build
	python -m build

clean :
	rm -rf build
	rm -rf dist
	rm -rf pccc.egg-info

commit :
	pre-commit run --all-files

lint :
	pytest --lint-only --black --flake8 --pydocstyle

pip :
	pip install -r requirements.txt

test:
	pytest --cov pccc --cov-report term

upload:
	python3 -m twine upload --verbose --repository pypi dist/*

upload-test:
	python3 -m twine upload --verbose --repository testpypi dist/*
