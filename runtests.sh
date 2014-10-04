#!/usr/bin/env bash

PYTHON_VERSIONS="2.7 3.2"

for VERSION in $PYTHON_VERSIONS
do
    PYTHON=$(which python$VERSION) make
done
