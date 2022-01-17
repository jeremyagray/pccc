#!/bin/bash
#
#***********************************************************************
#
# pccc, the Python Conventional Commit Checker.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright 2020-2022 Jeremy A Gray <gray@flyquackswim.com>.
#
#***********************************************************************

grep='/usr/bin/grep'
sed='/usr/bin/sed'

pip freeze | ${sed} 's/ @ .*-\(.*\)\(-py[23]\|-cp39-cp39\|-cp36\|\.tar\).*$/==\1/' | ${grep} -v '\(poetry\|pccc\)'
