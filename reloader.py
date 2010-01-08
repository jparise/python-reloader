# Python Module Reloader
#
# Copyright (c) 2009, 2010 Jon Parise <jon@indelible.org>
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

import builtins
import os
import sys
import queue
import imp
import time
import threading
from collections import OrderedDict

__author__  = 'Jon Parise <jon@indelible.org>'
__version__ = '0.1'

_win = (sys.platform == 'win32')
_baseimport = builtins.__import__
_modules = OrderedDict()

class ModuleMonitor(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.mtimes = {}
        self.queue = queue.Queue()

    def run(self):
        while True:
            self._scan()
            time.sleep(1)

    def _scan(self):
        # We're only interested in file-based modules (not C extensions).
        modules = [m.__file__ for m in sys.modules.values()
                if '__file__' in m.__dict__]

        for filename in modules:
            # We're only interested in the source .py files.
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                filename = filename[:-1]

            # stat() the file.  This might fail if the module is part of a
            # bundle (.egg).  We simply skip those modules because they're
            # not really reloadable anyway.
            try:
                stat = os.stat(filename)
            except OSError:
                continue

            # Check the modification time.  We need to adjust on Windows.
            mtime = stat.st_mtime
            if _win:
                mtime -= stat.st_ctime

            # If this is a new file, just register its mtime and move on.
            if filename not in self.mtimes:
                self.mtimes[filename] = mtime
                continue

	        # If this file's mtime has changed, queue it for reload.
            if mtime != self.mtimes[filename]:
                self.queue.put(filename)

            self.mtimes[filename] = mtime

class Reloader(object):

    def __init__(self, reload=imp.reload):
        self.reload = reload
        self.monitor = ModuleMonitor()
        self.monitor.start()

    def poll(self):
        filenames = set()
        while not self.monitor.queue.empty():
            try:
                filenames.add(self.monitor.queue.get_nowait())
            except queue.Empty:
                break
        if filenames:
            self._reload(filenames)

    def _reload(self, filenames):
        reloading = False
        for mod in _modules:
            # Toggle the reloading flag once we reach our first filename.
            if not reloading and mod.__file__ in filenames:
                reloading = True
            # Reload all later modules in the collection, as well.
            if reloading:
                self.reload(mod)

def _import(name, globals=None, locals=None, fromlist=None, level=None):
    """Local, reloader-aware __import__() replacement function"""
    mod = _baseimport(name, globals, locals, fromlist, level)
    if mod and '__file__' in mod.__dict__:
        _modules[mod] = mod.__file__
    return mod

def enable():
    """Enable global module reloading"""
    builtins.__import__ = _import

def disable():
    """Disable global module reloading"""
    builtins.__import__ = _baseimport
    _modules.clear()

if __name__ == '__main__':
    enable()
    import a    # imports sys
    import b    # imports a

    def reload(m):
        print("Reloading " + m.__file__)
        imp.reload(m)

    r = Reloader(reload=reload)
    while True:
        r.poll()
        time.sleep(1)
