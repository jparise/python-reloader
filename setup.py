from distutils.core import setup

version = __import__('reloader').__version__

setup(
    name = 'reloader',
    version = version,
    description = 'Automatic Python Module Reloader',
    author = 'Jon Parise',
    author_email = 'jon@indelible.org',
    classifiers = ['Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
    py_modules = ['reloader'],
)
