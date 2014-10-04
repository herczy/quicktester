PYTHON ?= $(shell which python)
NOSE = $(PYTHON) $(shell which nosetests)

.PHONY: all
all: unittest

.PHONY: unittest
unittest:
	$(NOSE)
