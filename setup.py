#!/usr/bin/env python

from distutils.core import setup

version = __import__('reloader').__version__

setup(
    name = 'reloader',
    version = version,
    description = 'Dependency-based Python module reloader',
    author = 'Jon Parise',
    author_email = 'jon@indelible.org',
    license = "MIT License",
    url = "https://github.com/jparise/python-reloader",
    classifiers = ['Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Development Status :: 4 - Beta',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
    py_modules = ['reloader'],
)
