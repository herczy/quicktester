PYTHON ?= $(shell which python) -B
NOSE = $(PYTHON) $(shell which nosetests)
BEHAVE = $(PYTHON) $(shell which behave)

.PHONY: all
all: unittest features

.PHONY: unittest
unittest:
	$(NOSE)

.PHONY: features
features:
	$(BEHAVE) --tags ~@work-in-progress
