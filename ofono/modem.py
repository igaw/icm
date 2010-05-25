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

import collections
import dbus_object

class Modem(dbus_object.dbus_object):
    def __init__(self, bus, uid):
        dbus_object.dbus_object.__init__(self, bus, "org.ofono", uid, "ofono_modem")

        self._modem_attr = collections.defaultdict(lambda: "<missing>")
        self._sim_manager_attr = collections.defaultdict(lambda: "<missing>")

        self.register_interface("org.ofono.Modem", self._modem_attr)

        self.update_properties()

    def add_interface(self, name):
        if name == "org.ofono.SimManager":
            self._sim_manager_attr = collections.defaultdict(lambda: "<missing>")
            self.register_interface("org.ofono.SimManager", self._sim_manager_attr)
            self.update_properties("org.ofono.SimManager")

    def remove_interface(self, name):
        if name == "org.ofono.SimManager":
            self._sim_manager_attr = collections.defaultdict(lambda: "<missing>")
            self.unregister_interface("org.ofono.SimManager")

    @property
    def uid(self):
        return self._uid

    #######################################
    # Modem Interface
    #######################################
    @property
    def modem_attributes(self):
        return self._modem_attr

    @property
    def Powered(self):
        return self._modem_attr["Powered"]

    @Powered.setter
    def Powered(self, enabled):
        self.get_interface("org.ofono.Modem").SetProperty("Powered", enabled)

    @property
    def Name(self):
        return str(self._modem_attr["Name"])

    @property
    def Manufacturer(self):
        return str(self._modem_attr["Manufacturer"])

    @property
    def Model(self):
        return str(self._modem_attr["Model"])

    @property
    def Revision(self):
        return str(self._modem_attr["Revision"])

    @property
    def Serial(self):
        return str(self._modem_attr["Serial"])

    @property
    def Interfaces(self):
        return self._modem_attr["Interfaces"]

    #######################################
    # SimManager Interface
    #######################################
    def EnterPin(self, type, pin):
        self.get_interface("org.ofono.SimManager").EnterPin(type, pin)

    @property
    def SubscriberIdentity(self):
        return str(self._sim_manager_attr["SubscriberIdentity"])

    @property
    def MobileCountryCode(self):
        return self._sim_manager_attr["MobileCountryCode"]

    @property
    def MobileNetworkCode(self):
        return self._sim_manager_attr["MobileNetworkCode"]

    @property
    def SubscriberNumbers(self):
        return self._sim_manager_attr["SubscriberNumbers"]

    @property
    def ServiceNumbers(self):
        return self._sim_manager_attr["ServiceNumbers"]

    @property
    def PinRequired(self):
        return self._sim_manager_attr["PinRequired"]

    @property
    def LockedPins(self):
        return self._sim_manager_attr["LockedPins"]
