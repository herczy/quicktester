#!/usr/bin/env bash

PYTHON_VERSIONS="2 3"

for VERSION in $PYTHON_VERSIONS
do
    PYTHON="$(which python$VERSION)" make
done
