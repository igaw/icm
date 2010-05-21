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

import logging

import collections
import dbus_object
import connman.device
import gobject

class Technology(dbus_object.dbus_object):
    __gsignals__ = {
        "add-device": (gobject.SIGNAL_RUN_FIRST,
                       gobject.TYPE_NONE,
                       (object,)),
        "remove-device": (gobject.SIGNAL_RUN_FIRST,
                          gobject.TYPE_NONE,
                          (object,)),
        }

    def __init__(self, bus, uid):
        dbus_object.dbus_object.__init__(self, bus, "org.moblin.connman", uid, "connman_technology")

        self._attr = collections.defaultdict(lambda: "<missing>")
        self._devices = {}

        self.register_interface("org.moblin.connman.Technology", self._attr)
        self.connect("property-changed", self.property_changed)
        self.update_properties()

    def get_devices(self):
        return self._devices.values()

    def property_changed(self, object, key, value):
        if key == "connman_technology_devices":
            self.handle_devices(value)

    def handle_devices(self, devices):
        # remove all devices which disappeared
        for path in self._devices.keys():
            if path not in devices:
                logging.debug("remove %s" % (path))
                self.emit("remove-device", self._devices[path])
                del self._devices[path]

        # now add all new devices
        for path in devices:
            if path not in self._devices.keys():
                logging.debug("add %s" % (path))
                self._devices[path] = connman.device.Device(self._bus, path)
                self.emit("add-device", self._devices[path])

    @property
    def uid(self):
        return self._uid

    @property
    def attributes(self):
        return self._attr

    #############################################################################

    @property
    def State(self):
        return self._attr["State"]

    @property
    def Name(self):
        return self._attr["Name"]

    @property
    def Devices(self):
        return self._attr["Devices"]
