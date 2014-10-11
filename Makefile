PYTHON ?= $(shell which python)
PYTHONOPTIONS ?= -B -s
NOSE = $(PYTHON) $(PYTHONOPTIONS) $(shell which nosetests)
BEHAVE = $(PYTHON) $(PYTHONOPTIONS) $(shell which behave)

.PHONY: all
all: unittest features

.PHONY: unittest
unittest:
	$(NOSE)

.PHONY: features
features:
	$(BEHAVE) --tags ~@work-in-progress
