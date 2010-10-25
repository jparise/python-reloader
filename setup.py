from distutils.core import setup

version = __import__('reloader').__version__

setup(
    name = 'Reloader',
    version = version,
    description = 'Dependency-based Python module reloader',
    author = 'Jon Parise',
    author_email = 'jon@indelible.org',
    license = "MIT License",
    url = "http://www.indelible.org/ink/python-reloading/",
    classifiers = ['Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
    py_modules = ['reloader'],
)
