#! /usr/bin/env python
import sys

extra = {}

try:
    from setuptools import setup
    if sys.version_info < (2, 7):
        extra['install_requires'] = ['argparse']
    if sys.version_info >= (3,):
        extra['use_2to3'] = True
except ImportError:
    from distutils.core import setup
    if sys.version_info < (2, 7):
        extra['dependencies'] = ['argparse']


setup(name               = 'shovel',
    version              = '0.3.0',
    description          = 'Not Rake, but Shovel',
    long_description     = 'Execute python functions as tasks',
    url                  = 'http://github.com/seomoz/shovel',
    author               = 'Dan Lecocq',
    author_email         = 'dan@moz.com',
    license              = "MIT License",
    keywords             = 'tasks, shovel, rake',
    packages             = ['shovel'],
    package_dir          = {'shovel': 'shovel'},
    package_data         = {'shovel': ['templates/*.tpl', 'static/css/*']},
    include_package_data = True,
    scripts              = ['bin/shovel'],
    setup_requires       = ['nose>=1.3'],
    test_suite           = 'nose.collector',
    tests_require        = ['nose>=1.3', 'path.py>=5.0', 'coverage>=3.7'],
    classifiers          = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
    ],
    **extra
)
