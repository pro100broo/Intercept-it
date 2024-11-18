SHELL := /bin/bash

app-build:
	python3 setup.py install

app-build-clean:
	python3 setup.py clean --all install clean --all
	rm -rf build
	rm -rf dist
	rm -rf sec_cx.egg-info
