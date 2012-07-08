import sys
sys.path.append("..")

import reloader
reloader.enable()

from monitor import Reloader
import another
import time

r = Reloader()

while True:
    another.doit()
    r.poll()
    time.sleep(1)
