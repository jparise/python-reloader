#!/usr/bin/env python

from setuptools import setup

version = __import__('reloader').__version__

setup(
    name='reloader',
    version=version,
    description='Dependency-based Python module reloader',
    author='Jon Parise',
    author_email='jon@indelible.org',
    license="MIT License",
    url="https://github.com/jparise/python-reloader",
    download_url=(
        'https://github.com/jparise/python-reloader/tarball/' + version),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    py_modules=['reloader'],
    test_suite='tests',
    zip_safe=True,
)
