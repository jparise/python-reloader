Python Module Reloader
======================

|Build Status| |PyPI Version| |Python Versions|

This library implements a dependency-based module reloader for Python.  Unlike
the builtin `reload()`_ function, this reloader will reload the requested
module *and all other modules that are dependent on that module*.

A detailed discussion of the reloader's implementation is available here:

    http://www.indelible.org/ink/python-reloading/

.. |Build Status| image:: https://secure.travis-ci.org/jparise/python-reloader.svg
   :target: http://travis-ci.org/jparise/python-reloader
.. |PyPI Version| image:: https://img.shields.io/pypi/v/python-reloader.svg
   :target: https://pypi.python.org/pypi/python-reloader
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/python-reloader.svg
   :target: https://pypi.python.org/pypi/python-reloader

Usage
-----

The reloader works by tracking dependencies between imported modules.  It must
first be enabled in order to track those dependencies.  The reloader has no
dependency information for modules that were imported before it was enabled or
after it is disabled, so you'll probably want to enable the reloader early in
your application's startup process.

.. code-block:: python

    import reloader
    reloader.enable()

    # Import additional modules
    import module1
    import module2

To manually reload an imported module, pass it to the reloader's ``reload()``
method:

.. code-block:: python

    import example
    reloader.reload(example)

Note that you must pass the module object itself and not a string containing
the module's name.  If you only have the module's name, you can fetch the
module object from the global ``sys.modules`` dictionary:

.. code-block:: python

    reloader.reload(sys.modules['example'])

You can also query a module's dependencies for informational or debugging
purposes:

.. code-block:: python

    reloader.get_dependencies(example)

You can disable the reloader's dependency tracking at any time:

.. code-block:: python

    reloader.disable()

Blacklisting Modules
--------------------

There may be times when you don't want a module and its dependency hierarchy
to be reloaded.  The module might rarely change and be expensive to import.
To support these cases, you can explicitly "blacklist" modules from the
reloading process using the ``blacklist`` argument to ``enable()``.

.. code-block:: python

    reloader.enable(blacklist=['os', 'ConfigParser'])

The blacklist can be any iterable listing the fully-qualified names of modules
that should be ignored.  Note that blacklisted modules will still appear in
the dependency graph for completeness; they will just not be reloaded.

An Interactive Example
----------------------

This example demonstrates how easily the reloader can be used from the
interactive Python interpretter.  Imagine you have the module ``example.py``
open in a text editor, and it contains the following:

.. code-block:: python

    print "I am example.py"

Our interactive session starts like this:

.. code-block:: python

    >>> import reloader
    >>> reloader.enable()
    >>> import example
    I am example.py

Now modify ``example.py`` in your text editor.  You can then reload the
``example`` in your interactive session:

.. code-block:: python

    >>> reloader.reload(example)
    I am the modified example.py

This is a simplistic example that doesn't fully demonstrate the power of the
reloader's dependency-based module tracking, but it hopefully illustrates the
basic usage and utility of the system.

The __reload__() Callback
-------------------------

If a module has a ``__reload__()`` function, it will be called with a copy of
the original module's dictionary after it has been reloaded.  This provides a
convenient mechanism for preserving state between reloads.

Consider a module named ``counts`` that contains the following code:

.. code-block:: python

    COUNTER = 0

The module's ``COUNTER`` variable will be reset to 0 when the module is
reloaded:

.. code-block:: python

    >>> import counts
    >>> counts.COUNTER += 1
    >>> counts.COUNTER
    1
    >>> reloader.reload(counts)
    >>> counts.COUNTER += 1
    1

We can preserve the value of ``COUNTER`` across reloads by adding a
``__reload__()`` function to the ``counts`` module:

.. code-block:: python

    def __reload__(state):
        global COUNTER
        COUNTER = state['COUNTER']

Now when we reload ``counts``:

.. code-block:: python

    >>> import counts
    >>> counts.COUNTER += 1
    >>> counts.COUNTER
    1
    >>> reloader.reload(counts)
    >>> counts.COUNTER += 1
    >>> counts.COUNTER
    2

.. _`reload()`: http://docs.python.org/library/functions.html#reload
