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

import gobject
import logging

import collections
import dbus_object

import ofono.primarycontext

class Modem(dbus_object.dbus_object):
    __gsignals__ = {
        "add-primarycontext": (gobject.SIGNAL_RUN_FIRST,
                               gobject.TYPE_NONE,
                               (object,)),
        "remove-primarycontext": (gobject.SIGNAL_RUN_FIRST,
                                  gobject.TYPE_NONE,
                                  (object,)),
        }

    def __init__(self, bus, uid):
        dbus_object.dbus_object.__init__(self, bus, "org.ofono", uid, "ofono_modem")

        self._primarycontexts = {}

        self._modem_attr = collections.defaultdict(lambda: "<missing>")
        self._sim_manager_attr = collections.defaultdict(lambda: "<missing>")
        self._registration_attr = collections.defaultdict(lambda: "<missing>")
        self._gprs_attr = collections.defaultdict(lambda: "<missing>")

        self.register_interface("org.ofono.Modem", self._modem_attr)
        self.connect("property-changed", self.property_changed)

        self.update_properties()

    def get_primarycontexts(self):
        return self._primarycontexts.values()

    def property_changed(self, object, key, value):
        if key == "ofono_modem_primarycontexts":
            self.handle_primarycontexts(value)

    def handle_primarycontexts(self, contexts):
        # remove all primary data contexts which disappeared
        for path in self._primarycontexts.keys():
            if path not in contexts:
                logging.debug("remove primary contexts %s" % (path))
                self.emit("remove-primarycontext", self._primarycontexts[path])
                del self._primarycontexts[path]

        # now add all new primary data contexts
        for path in contexts:
            if path not in self._primarycontexts.keys():
                logging.debug("add primarycontexts %s" % (path))
                self._primarycontexts[path] = ofono.primarycontext.PrimaryDataContext(self._bus, path)
                self.emit("add-primarycontext", self._primarycontexts[path])

    def add_interface(self, name):
        if name == "org.ofono.SimManager":
            self._sim_manager_attr = collections.defaultdict(lambda: "<missing>")
            self.register_interface(name, self._sim_manager_attr)
            self.update_properties(name)
        elif name == "org.ofono.NetworkRegistration":
            self._registration_attr = collections.defaultdict(lambda: "<missing>")
            self.register_interface(name, self._registration_attr)
            self.update_properties(name)
        elif name == "org.ofono.DataConnectionManager":
            self._gprs_attr = collections.defaultdict(lambda: "<missing>")
            self.register_interface(name, self._gprs_attr)
            self.update_properties(name)

    def remove_interface(self, name):
        if name == "org.ofono.SimManager":
            self._sim_manager_attr = collections.defaultdict(lambda: "<missing>")
            self.unregister_interface(name)
        elif name == "org.ofono.NetworkRegistration":
            self._registration_attr = collections.defaultdict(lambda: "<missing>")
            self.unregister_interface(name)
        elif name == "org.ofono.DataConnectionManager":
            self._gprs_attr = collections.defaultdict(lambda: "<missing>")
            self.unregister_interface(name)

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

    #######################################
    # NetworkRegistration Interface
    #######################################

    def Register(self):
        self.get_interface("org.ofono.NetworkRegistration").Register()

    def Deregister(self):
        self.get_interface("org.ofono.NetworkRegistration").Deregister()

    def ProposeScan(self):
        return self.get_interface("org.ofono.NetworkRegistration").ProposeScan()

    @property
    def Mode(self):
        return str(self._registration_attr["Mode"])

    @property
    def Status(self):
        return str(self._registration_attr["Status"])

    @property
    def LocationAreaCode(self):
        return str(self._registration_attr["LocationAreaCode"])

    @property
    def CellId(self):
        return int(self._registration_attr["CellId"])

    @property
    def Technology(self):
        return str(self._registration_attr["Technology"])

    @property
    def Name(self):
        return str(self._registration_attr["Name"])

    @property
    def Strength(self):
        return int(self._registration_attr["Strength"])

    @property
    def BaseStation(self):
        return str(self._registration_attr["BaseStation"])

    @property
    def Operators(self):
        return self._registration_attr["Operators"]

    #######################################
    # DataConnectionManager Interface
    #######################################

    def DeactivateAll(self):
        self.get_interface("org.ofono.DataConnectionManager").DeactivateAll()

    def CreateContext(self, name, type):
        return self.get_interface("org.ofono.DataConnectionManager").CreateContext(name, type)

    def RemoveContext(self, context):
        self.get_interface("org.ofono.DataConnectionManager").RemoveContext()

    @property
    def Attached(self):
        return self._gprs_attr["Attached"]

    @property
    def RoamingAllowed(self):
        return self._gprs_attr["RoamingAllowed"]

    @property
    def GPRS_Powered(self):
        return self._gprs_attr["Powered"]
