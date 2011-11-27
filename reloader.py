# Python Module Reloader
#
# Copyright (c) 2009, 2010, 2011 Jon Parise <jon@indelible.org>
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

try:
    import builtins
except ImportError:
    #python 2.x
    import __builtin__ as builtins

import imp
import sys

__author__ = 'Jon Parise <jon@indelible.org>'
__version__ = '0.2'

__all__ = ('enable', 'disable', 'get_dependencies', 'reload')

_baseimport = builtins.__import__
_dependencies = dict()
_parent = None
_existing_modules = None

def enable(ignore_existing_dependencies=False):
    """Enable global module dependency tracking."""
    global _existing_modules
    if ignore_existing_dependencies:
      _existing_modules = list(sys.modules.values())
    else:
      _existing_modules = []
    builtins.__import__ = _import

def disable():
    """Disable global module dependency tracking."""
    builtins.__import__ = _baseimport
    _dependencies.clear()
    global _parent
    _parent = None
    global _existing_modules
    _existing_modules = None

def get_dependencies(m):
    """Get the dependency list for the given imported module."""
    return _dependencies.get(m.__name__, None)

def _deepcopy_module_dict(m):
    """Make a deep copy of a module's dictionary."""
    import copy

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

def _import(name, globals=None, locals=None, fromlist=None, level=-1):
    """__import__() replacement function that tracks module dependencies."""
    # Track our current parent module.  This is used to find our current place
    # in the dependency graph.
    global _parent
    parent = _parent
    _parent = name

    # Perform the actual import using the base import function.  We get the
    # module directly from sys.modules because the import function only
    # returns the top-level module reference for a nested import statement
    # (e.g. `import package.module`).
    base_returned_module = _baseimport(name, globals, locals, fromlist, level)
    
    # Don't add this module as a dependency if it was imported before
    # enable() was called. This allows the user an explicit way to
    # prevent modules from being reloaded.
    if not base_returned_module in _existing_modules:
      m = sys.modules.get(name, None)

      # If we have a parent (i.e. this is a nested import) and this is a
      # reloadable (source-based) module, we append ourself to our parent's
      # dependency list.
      if parent is not None and hasattr(m, '__file__'):
          l = _dependencies.setdefault(parent, [])
          l.append(m)

    # Lastly, we always restore our global _parent pointer.
    _parent = parent

    return base_returned_module
