# This file is part of rentswatch-scraper.
# https://github.com/jplusplus/rentswatch-scraper

# Licensed under the LGPL license:
# http://www.opensource.org/licenses/LGPL-license
# Copyright (c) 2015, pirhoo <hello@pirhoo.com>
VENV = venv
ENV = venv/bin/activate
DOCKER_NAME = rentswatch-scraper
DOCKER_AUTHOR = pirhoo

$(VENV):
	virtualenv venv --no-site-packages --distribute --prompt=rentswatch

install: $(VENV)

# lists all available targets
list:
	@sh -c "$(MAKE) -p no_targets__ | awk -F':' '/^[a-zA-Z0-9][^\$$#\/\\t=]*:([^=]|$$)/ {split(\$$1,A,/ /);for(i in A)print A[i]}' | grep -v '__\$$' | grep -v 'make\[1\]' | grep -v 'Makefile' | sort"
# required for list
no_targets__:

# install all dependencies (do not forget to create a virtualenv first)
setup:
	@pip install -U -e .\[tests\]

publish:
	python setup.py register sdist upload
