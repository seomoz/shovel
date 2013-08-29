#! /usr/bin/env python
import sys

extra = {}
try:
	from setuptools import setup
        if sys.version_info < (2,7):
                extra['install_requires'] = ['argparse']
	if sys.version_info >= (3,):
		extra['use_2to3'] = True
except ImportError:
	from distutils.core import setup
        if sys.version_info < (2,7):
                extra['dependencies'] = ['argparse']

setup(name               = 'shovel',
	version              = '0.1.10',
	description          = 'Not Rake, but Shovel',
	long_description     = 'Execute python functions as tasks',
	url                  = 'http://github.com/seomoz/shovel',
	author               = 'Dan Lecocq',
	author_email         = 'dan@seomoz.org',
    license              = "MIT License",
	keywords             = 'tasks, shovel, rake',
	packages             = ['shovel'],
	package_dir          = {'shovel': 'shovel'},
    package_data         = {'shovel': ['templates/*.tpl', 'static/css/*']},
    include_package_data = True,
	scripts              = ['bin/shovel', 'bin/shovel-server', 'bin/shovel-campfire'],
	classifiers          = [
        'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Intended Audience :: Developers',
		'Operating System :: OS Independent'
	],
	**extra
)
