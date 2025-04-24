.PHONY: install run clean

# Detect OS
#
OS := $(shell uname -s 2>/dev/null || echo Windows)

ifeq ($(OS),Windows)
	VENV_ACTIVATE = venv\Scripts\activate
	PYTHON = python
	RM = rmdir /S /Q
else
	VENV_ACTIVATE = . venv/bin/activate
	PYTHON = python3
	RM = rm -rf
endif


install:
	$(PYTHON) -m venv venv
	$(VENV_ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt

run:
	$(VENV_ACTIVATE) && jupyter notebook

clean:
	$(RM) venv
