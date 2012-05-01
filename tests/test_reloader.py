from unittest import TestCase
import sys
import os

sys.dont_write_bytecode = True


class ReloaderTest(TestCase):

    def test_import(self):
        import reloader

    def test_reload(self):
        import reloader
        reloader.enable()

        self.write_module('testmodule', "def func(): return 'Some code.'\n")
        import testmodule
        self.assertEqual('Some code.', testmodule.func())

        self.write_module('testmodule', "def func(): return 'New code.'\n")
        reloader.reload(testmodule)
        self.assertEqual('New code.', testmodule.func())

        self.write_module('testmodule', "def func(): return 'More code.'\n")
        reloader.reload(testmodule)
        self.assertEqual('More code.', testmodule.func())

    def tearDown(self):
        self.remove_module('testmodule')

    def write_module(self, module_name, str):
        f = open(self.get_module_filename(module_name), 'w')
        f.write(str)
        f.close()

    def remove_module(self, module_name):
        filename = self.get_module_filename(module_name)

        if os.path.exists(filename):
            os.unlink(filename)

    def get_module_filename(self, module_name):
        return os.path.join(os.path.dirname(__file__), module_name + '.py')
