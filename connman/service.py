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

class Service(dbus_object.dbus_object):
    def __init__(self, bus, uid):
        dbus_object.dbus_object.__init__(self, bus, "org.moblin.connman", uid, "connman_service")

        self._attr = collections.defaultdict(lambda: "<missing>")
        self.register_interface("org.moblin.connman.Service", self._attr)

        self.update_properties()

    def srv_connect(self):
        self.get_interface("org.moblin.connman.Service").Connect()

    def srv_disconnect(self):
        self.get_interface("org.moblin.connman.Service").Disconnect()

    def __repr__(self):
        return "<%s %s %s>" % (self._name, self.Name, self.uid)

    @property
    def uid(self):
        return self._uid

    @property
    def attributes(self):
        return self._attr

    #############################################################################

    @property
    def Error(self):
        return self._attr["Error"]

    @property
    def Name(self):
        return self._attr["Name"]

    @property
    def Type(self):
        return self._attr["Type"]

    @property
    def Mode(self):
        return self._attr["Mode"]

    @property
    def Security(self):
        return self._attr["Security"]

    @property
    def Passphrase(self):
        return self._attr["Passphrase"]

    @Passphrase.setter
    def Passphrase(self, pwd):
        self.get_interface("org.moblin.connman.Service").SetProperty("Passphrase", pwd)

    @property
    def Strength(self):
        return self._attr["Strength"]

    @property
    def Immutable(self):
        return self._attr["Immutable"]

    @Immutable.setter
    def Immutable(self, value):
        self.get_interface("org.moblin.connman.Service").SetProperty("Immutable", value)

    @property
    def AutoConnect(self):
        return self._attr["AutoConnect"]

    @AutoConnect.setter
    def AutoConnect(self, value):
        self.get_interface("org.moblin.connman.Service").SetProperty("AutoConnect", value)

    @property
    def SetupRequired(self):
        return self._attr["SetupRequired"]

    @property
    def APN(self):
        return self._attr["APN"]

    @APN.setter
    def APN(self, apn):
        self.get_interface("org.moblin.connman.Service").SetProperty("APN", apn)

    @property
    def MCC(self):
        return self._attr["MCC"]

    @property
    def MMC(self):
        return self._attr["MMC"]

    @property
    def Roaming(self):
        return self._attr["Roaming"]

    @property
    def Nameservers(self):
        return self._attr["Nameservers"]

    @property
    def IPv4(self):
        return self._attr["IPv4"]

    @property
    def IPv4_Configuration(self):
        return self._attr["IPv4.Configuration"]

    @property
    def Proxy(self):
        return self._attr["Proxy"]

    @property
    def Ethernet(self):
        return self._attr["Ethernet"]

    @property
    def Ethernet_Address(self):
        return self._attr["Ethernet"]["Address"]

    @property
    def Ethernet_Interface(self):
        return self._attr["Ethernet"]["Interface"]

    @property
    def Ethernet_MTU(self):
        return int(self._attr["Ethernet"]["MTU"])

    @property
    def Ethernet_Method(self):
        return self._attr["Ethnernet"]["Method"]

    @property
    def State(self):
        return self._attr["State"]
