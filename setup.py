#!/usr/bin/env python

import sys

from setuptools import setup

setup(
    name='shovel',
    version='0.5.0',
    description='Not Rake, but Shovel',
    long_description='Execute python functions as tasks',
    url='http://github.com/seomoz/shovel',
    author='Dan Lecocq',
    author_email='dan@moz.com',
    license="MIT License",
    keywords='tasks, shovel, rake',
    packages=['shovel'],
    package_dir={'shovel': 'shovel'},
    package_data={'shovel': ['templates/*.tpl', 'static/css/*']},
    include_package_data=True,
    # scripts=['bin/shovel'],
    entry_points={'console_scripts': ['shovel = shovel:run']},
    setup_requires=['nose>=1.3'],
    test_suite='nose2.collector.collector',
    tests_require=['nose>=1.3', 'path.py>=5.0', 'coverage>=3.7'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
    ],
)
