# Python Module Reloader
#
# Copyright (c) 2009-2015 Jon Parise <jon@indelible.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Python Module Reloader"""

import copy
import imp
import sys
import types

# Python 3 has builtins.__import__, but
# Python 2 has __builtin__.__import__
if sys.version_info[0] >= 3:
    import builtins as system_builtins
else:
    import __builtin__ as system_builtins

__author__ = 'Jon Parise <jon@indelible.org>'
__version__ = '0.7.dev0'

__all__ = ('enable', 'disable', 'get_dependencies', 'reload')

_baseimport = system_builtins.__import__
_blacklist = None
_dependencies = dict()
_parent = None

# Jython doesn't have imp.reload().
if not hasattr(imp, 'reload'):
    imp.reload = reload  # noqa

# PEP 328 changed the default level to 0 in Python 3.3.
_default_level = -1 if sys.version_info < (3, 3) else 0


def enable(blacklist=None):
    """Enable global module dependency tracking.

    A blacklist can be specified to exclude specific modules (and their import
    hierachies) from the reloading process.  The blacklist can be any iterable
    listing the fully-qualified names of modules that should be ignored.  Note
    that blacklisted modules will still appear in the dependency graph; they
    will just not be reloaded.
    """
    global _blacklist
    system_builtins.__import__ = _import
    if blacklist is not None:
        _blacklist = frozenset(blacklist)


def disable():
    """Disable global module dependency tracking."""
    global _blacklist, _parent
    system_builtins.__import__ = _baseimport
    _blacklist = None
    _dependencies.clear()
    _parent = None


def get_dependencies(m):
    """Get the dependency list for the given imported module."""
    name = m.__name__ if isinstance(m, types.ModuleType) else m
    return _dependencies.get(name, None)


def _deepcopy_module_dict(m):
    """Make a deep copy of a module's dictionary."""
    # We can't deepcopy() everything in the module's dictionary because some
    # items, such as '__builtins__', aren't deepcopy()-able.  To work around
    # that, we start by making a shallow copy of the dictionary, giving us a
    # way to remove keys before performing the deep copy.
    d = vars(m).copy()
    del d['__builtins__']
    return copy.deepcopy(d)


def _reload(m, visited):
    """Internal module reloading routine."""
    name = m.__name__

    # If this module's name appears in our blacklist, skip its entire
    # dependency hierarchy.
    if _blacklist and name in _blacklist:
        return

    # Start by adding this module to our set of visited modules.  We use this
    # set to avoid running into infinite recursion while walking the module
    # dependency graph.
    visited.add(m)

    # Start by reloading all of our dependencies in reverse order.  Note that
    # we recursively call ourself to perform the nested reloads.
    deps = _dependencies.get(name, None)
    if deps is not None:
        for dep in reversed(deps):
            if dep not in visited:
                _reload(dep, visited)

    # Clear this module's list of dependencies.  Some import statements may
    # have been removed.  We'll rebuild the dependency list as part of the
    # reload operation below.
    try:
        del _dependencies[name]
    except KeyError:
        pass

    # Because we're triggering a reload and not an import, the module itself
    # won't run through our _import hook below.  In order for this module's
    # dependencies (which will pass through the _import hook) to be associated
    # with this module, we need to set our parent pointer beforehand.
    global _parent
    _parent = name

    # If the module has a __reload__(d) function, we'll call it with a copy of
    # the original module's dictionary after it's been reloaded.
    callback = getattr(m, '__reload__', None)
    if callback is not None:
        d = _deepcopy_module_dict(m)
        imp.reload(m)
        callback(d)
    else:
        imp.reload(m)

    # Reset our parent pointer now that the reloading operation is complete.
    _parent = None


def reload(m):
    """Reload an existing module.

    Any known dependencies of the module will also be reloaded.

    If a module has a __reload__(d) function, it will be called with a copy of
    the original module's dictionary after the module is reloaded."""
    _reload(m, set())


def _import(name, globals=None, locals=None, fromlist=None,
            level=_default_level):
    """__import__() replacement function that tracks module dependencies."""
    # Track our current parent module.  This is used to find our current place
    # in the dependency graph.
    global _parent
    parent = _parent
    _parent = name

    # Perform the actual import work using the base import function.
    base = _baseimport(name, globals, locals, fromlist, level)

    if base is not None and parent is not None:
        m = base

        # We manually walk through the imported hierarchy because the import
        # function only returns the top-level package reference for a nested
        # import statement (e.g. 'package' for `import package.module`) when
        # no fromlist has been specified.  It's possible that the package
        # might not have all of its descendents as attributes, in which case
        # we fall back to using the immediate ancestor of the module instead.
        if fromlist is None:
            for component in name.split('.')[1:]:
                try:
                    m = getattr(m, component)
                except AttributeError:
                    m = sys.modules[m.__name__ + '.' + component]

        # If this is a nested import for a reloadable (source-based) module,
        # we append ourself to our parent's dependency list.
        if hasattr(m, '__file__'):
            deps = _dependencies.setdefault(parent, [])
            deps.append(m)

    # Lastly, we always restore our global _parent pointer.
    _parent = parent

    return base
