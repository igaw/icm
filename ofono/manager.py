#  IVI Connection Manager
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
import gobject

import collections
import dbus_object
import ofono.modem

class Manager(dbus_object.dbus_object):
    __gsignals__ = {
        "add-modem": (gobject.SIGNAL_RUN_FIRST,
                      gobject.TYPE_NONE,
                      (object,)),
        "remove-modem": (gobject.SIGNAL_RUN_FIRST,
                         gobject.TYPE_NONE,
                         (object,)),
        }

    def __init__(self, bus, uid):
        dbus_object.dbus_object.__init__(self, bus, "org.ofono", uid, "ofono_manager")

        self._attr = collections.defaultdict(lambda: "<missing>")
        self._modems = {}

        self.register_interface("org.ofono.Manager", self._attr)
        self.connect("property-changed", self.property_changed)
        self.update_properties()


    def get_modems(self):
        return self._modems.values()

    def property_changed(self, object, key, value):
        if key == "ofono_manager_modems":
            self.handle_modems(value)

    def handle_modems(self, modems):
        # remove all modems which disappeared
        for path in self._modems.keys():
            if path not in modems:
                logging.debug("remove modem %s" % (path))
                self.emit("remove-modem", self._modems[path])
                del self._modems[path]

        # now add all new modems
        for path in modems:
            if path not in self._modems.keys():
                logging.debug("add modem %s" % (path))
                self._modems[path] = ofono.modem.Modem(self._bus, path)
                self.emit("add-modem", self._modems[path])

    @property
    def uid(self):
        return self._uid

    @property
    def attributes(self):
        return self._attr

    #############################################################################

    @property
    def Modems(self):
        return self._attr["Modems"]
