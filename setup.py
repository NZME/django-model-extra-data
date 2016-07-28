#!//usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 NZME

from __future__ import unicode_literals, absolute_import

import codecs
import os
import re
import sys
from itertools import chain

from setuptools import setup, find_packages


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


install_requires = [
    'Django>=1.6',
    'json-encoder>=0.4.3',
]

extra_requires = {
    'rest_framework': [
        'djangorestframework',
    ],
}

if sys.version_info[0:2] < (3, 4):
    # required for python < 3.4
    extra_requires['rest_framework'].append('singledispatch>=3.4.0.3')

extra_requires['all'] = list(chain.from_iterable(extra_requires.values()))

setup(
    name='django-model-extra-data',
    version=find_version('django_model_extra_data', '__init__.py'),
    author='NZME',
    author_email='sysadmin@grabone.co.nz',
    url='https://github.com/NZME/django-model-extra-data',
    description='Flexible django model',
    long_description=read('README.rst'),
    setup_requires=['pytest-runner'],
    install_requires=install_requires,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
    ],
    extras_require=extra_requires,
    tests_require=[
        'pytest',
        'pytest-django',
    ]
)
