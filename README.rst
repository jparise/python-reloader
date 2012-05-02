Python Module Reloader
======================

.. image:: https://secure.travis-ci.org/jparise/python-reloader.png?branch=master
   :target: http://travis-ci.org/jparise/python-reloader

This library implements a dependency-based module reloader for Python.  Unlike
the builtin `reload()`_ function, this reloader will reload the requested
module *and all other modules that are dependent on that module*.

A detailed discussion of the reloader's implementation is available here:

    http://www.indelible.org/ink/python-reloading/

Usage
-----

The reloader works by tracking dependencies between imported modules.  It must
first be enabled in order to track those dependencies.  The reloader has no
dependency information for modules that were imported before it was enabled or
after it is disabled, so you'll probably want to enable the reloader early in
your application's startup process.

::

    import reloader
    reloader.enable()

    # Import additional modules
    import module1
    import module2

To manually reload an imported module, pass it to the reloader's ``reload()``
method::

    import example
    reloader.reload(example)

Note that you must pass the module object itself and not a string containing
the module's name.  If you only have the module's name, you can fetch the
module object from the global ``sys.modules`` dictionary::

    reloader.reload(sys.modules['example'])

You can also query a module's dependencies for informational or debugging
purposes::

    reloader.get_dependencies(example)

You can disable the reloader's dependency tracking at any time::

    reloader.disable()

An Interactive Example
----------------------

This example demonstrates how easily the reloader can be used from the
interactive Python interpretter.  Imagine you have the module ``example.py``
open in a text editor, and it contains the following::

    print "I am example.py"

Our interactive session starts like this::

    >>> import reloader
    >>> reloader.enable()
    >>> import example
    I am example.py

Now modify ``example.py`` in your text editor.  You can then reload the
``example`` in your interactive session::

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

Consider a module named ``counts`` that contains the following code::

    COUNTER = 0

The module's ``COUNTER`` variable will be reset to 0 when the module is
reloaded::

    >>> import counts
    >>> counts.COUNTER += 1
    >>> counts.COUNTER
    1
    >>> reloader.reload(counts)
    >>> counts.COUNTER += 1
    1

We can preserve the value of ``COUNTER`` across reloads by adding a
``__reload__()`` function to the ``counts`` module::

    def __reload__(state):
        global COUNTER
        COUNTER = state['COUNTER']

Now when we reload ``counts``::

    >>> import counts
    >>> counts.COUNTER += 1
    >>> counts.COUNTER
    1
    >>> reloader.reload(counts)
    >>> counts.COUNTER += 1
    >>> counts.COUNTER
    2

.. _`reload()`: http://docs.python.org/library/functions.html#reload
