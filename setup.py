#! /usr/bin/env python

try:
	from setuptools import setup
	extra = {
		'install_requires' : ['argparse']
	}
except ImportError:
	from distutils.core import setup
	extra = {
		'dependencies' : ['argparse']
	}

setup(name               = 'shovel',
	version              = '0.1.9',
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
