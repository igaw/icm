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
import gobject
import connman.network

class Device(dbus_object.dbus_object):
    __gsignals__ = {
        "add-network": (gobject.SIGNAL_RUN_FIRST,
                         gobject.TYPE_NONE,
                         (object,)),
        "remove-network": (gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            (object,)),
        }

    def __init__(self, bus, uid):
        dbus_object.dbus_object.__init__(self, bus, "org.moblin.connman", uid, "connman_device")

        self._attr = collections.defaultdict(lambda: "<missing>")
        self._networks = {}

        self.register_interface("org.moblin.connman.Device", self._attr)
        self.connect("property-changed", self.property_changed)
        self.update_properties()

    def get_networks(self):
        return self._networks.values()

    def property_changed(self, object, key, value):
        if key == "connman_device_networks":
            self.handle_networks(value)

    def handle_networks(self, networks):
        # remove all devices which disappeared
        for path in self._networks.keys():
            if path not in networks:
                logging.debug("remove device %s" % (path))
                self.emit("remove-network", self._networks[path])
                del self._networks[path]

        # now add all new devices
        for path in networks:
            if path not in self._networks.keys():
                logging.debug("add device %s" % (path))
                self._networks[path] = connman.network.Network(self._bus, path)
                self.emit("add-network", self._networks[path])

    def propose_scan(self):
        self.get_interface("org.moblin.connman.Device").ProposeScan()

    @property
    def uid(self):
        return self._uid

    @property
    def attributes(self):
        return self._attr

    #############################################################################

    @property
    def Address(self):
        return self._attr["Address"]

    @property
    def Name(self):
        return self._attr["Name"]

    @property
    def Type(self):
        return self._attr["Type"]

    @property
    def Interface(self):
        return self._attr["Interface"]

    @property
    def Powered(self):
        return self._attr["Powered"]

    @property
    def ScanInterval(self):
        return self._attr["ScanInterval"]

    @ScanInterval.setter
    def ScanInterval(self, interval):
        self.get_interface("org.moblin.connman.Device").SetProperty("ScanInterval", pwd)

    @property
    def Scanning(self):
        return self._attr["Scanning"]

    @property
    def Networks(self):
        return self._attr["Networks"]
