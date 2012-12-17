import os
import sys
import unittest

class ReloaderTests(unittest.TestCase):

    def setUp(self):
        self.modules = {}

        # Save the existing system bytecode setting so that it can
        # be restored later.  We need to disable bytecode writing
        # for our module-(re)writing tests.
        self._dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True

    def tearDown(self):
        # Clean up any modules that this test wrote.
        for name, filename in self.modules.items():
            if name in sys.modules:
                del sys.modules[name]
            if os.path.exists(filename):
                os.unlink(filename)

        # Restore the system bytecode setting.
        sys.dont_write_bytecode = self._dont_write_bytecode

    def test_import(self):
        import reloader
        self.assertTrue('reloader' in sys.modules)
        self.assertTrue(hasattr(reloader, 'enable'))

    def test_reload(self):
        import reloader
        reloader.enable()

        self.write_module('testmodule', "def func(): return 'Some code.'\n")
        import tests.testmodule
        self.assertEqual('Some code.', tests.testmodule.func())

        self.write_module('testmodule', "def func(): return 'New code.'\n")
        reloader.reload(tests.testmodule)
        self.assertEqual('New code.', tests.testmodule.func())

        self.write_module('testmodule', "def func(): return 'More code.'\n")
        reloader.reload(tests.testmodule)
        self.assertEqual('More code.', tests.testmodule.func())

        reloader.disable()

    def test_blacklist(self):
        import reloader
        reloader.enable(['blacklisted'])

        self.write_module('blacklisted', "def func(): return True\n")
        self.write_module('testmodule', "import tests.blacklisted\n")

        import tests.blacklisted, tests.testmodule

        reloader.disable()

    def write_module(self, name, contents):
        filename = os.path.join(os.path.dirname(__file__), name + '.py')
        self.modules['tests.' + name] = filename

        f = open(filename, 'w')
        f.write(contents)
        f.close()
