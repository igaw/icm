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

import collections
import dbus_object

class Network(dbus_object.dbus_object):
    def __init__(self, bus, uid):
        dbus_object.dbus_object.__init__(self, bus, "org.moblin.connman", uid, "connman_network")

        self._attr = collections.defaultdict(lambda: "<missing>")
        self.register_interface("org.moblin.connman.Network", self._attr)

        self.update_properties()

    @property
    def uid(self):
        return self._uid

    @property
    def attributes(self):
        return self._attr

    @property
    def wifi_ssid_hex(self):
        nr = ""
        for c in self._attr["WiFi.SSID"]:
            nr = "%s%x" % (nr, c)
        return nr

    #############################################################################

    @property
    def Address(self):
        return self._attr["Address"]

    @property
    def Connected(self):
        return self._attr["Connected"]

    @property
    def Strength(self):
        return self._attr["Strength"]

    @property
    def Device(self):
        return self._attr["Device"]

    @property
    def WiFi_SSID(self):
        return self._attr["WiFi.SSID"]

    @property
    def WiFi_Mode(self):
        return self._attr["WiFi.Mode"]

    @property
    def WiFi_Security(self):
        return self._attr["WiFi.Security"]

    @property
    def WiFi_Passphrase(self):
        return self._attr["WiFi.Passsphrase"]

