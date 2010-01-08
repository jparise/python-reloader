from distutils.core import setup

version = __import__('reloader').__version__

setup(
    name = 'reloader',
    version = version,
    description = 'Automatic Python Module Reloader',
    author = 'Jon Parise',
    author_email = 'jon@indelible.org',
    license = "MIT License",
    classifiers = ['Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
    py_modules = ['reloader'],
)
