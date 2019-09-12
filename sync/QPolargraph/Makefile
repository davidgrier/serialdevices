UIFILE := $(wildcard *.ui)
PYFILE := $(UIFILE:.ui=.py)
PYTHON = python
PYUIC = pyuic5

.PHONY: all test

all: $(PYFILE)

test: $(PYFILE)
	$(PYTHON) $(PYFILE)

clean: $(PYFILE)
	-rm $(PYFILE)

%.py: %.ui
	$(PYUIC) $< -x -o $@
