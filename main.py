#  GENIVI Connection Manager
#
#  Copyright (C) 2010  BMW Car IT GmbH. All rights reserved.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License version 2 as
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

#!/usr/bin/env python
import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
import sys

import trace
import logging
import traceback

import manager
import gcm

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    name = dbus.service.BusName("org.genivi.gcm", bus)

    mgr = manager.ManagerWrapper(bus)
    cm = gcm.GCM(bus, mgr)

    mainloop = gobject.MainLoop()
    mainloop.run()

if __name__ == '__main__':
    FORMAT = "%(levelname)s %(filename)-15s %(lineno)3d %(funcName)-20s: %(message)s"
    logging.basicConfig(level = logging.DEBUG, format = FORMAT)

    tracer = trace.Trace(ignoredirs=[sys.prefix, sys.exec_prefix],
                         trace=0,
                         count=1)
    try:
        tracer.run('main()')
    except KeyboardInterrupt:
        r = tracer.results()
        r.write_results(show_missing=True, coverdir="/tmp/gcm")
