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

import connman.service
import connman.technology

class Manager(dbus_object.dbus_object):
    __gsignals__ = {
        "add-service": (gobject.SIGNAL_RUN_FIRST,
                        gobject.TYPE_NONE,
                        (object,)),
        "remove-service": (gobject.SIGNAL_RUN_FIRST,
                           gobject.TYPE_NONE,
                           (object,)),
        "add-technology": (gobject.SIGNAL_RUN_FIRST,
                           gobject.TYPE_NONE,
                           (object,)),
        "remove-technology": (gobject.SIGNAL_RUN_FIRST,
                              gobject.TYPE_NONE,
                              (object,)),
        }

    def __init__(self, bus, uid):
        dbus_object.dbus_object.__init__(self, bus, "org.moblin.connman", uid, "connman_manager")

        self._attr = collections.defaultdict(lambda: "<missing>")
        self._services = {}
        self._technologies = {}

        self.register_interface("org.moblin.connman.Manager", self._attr)
        self.connect("property-changed", self.property_changed)

        self.update_properties()

    def get_services(self):
        return self._services.values()

    def get_technologies(self):
        return self._technologies.values()

    def property_changed(self, object, key, value):
        if key == "connman_manager_services":
            self.handle_services(value)
        elif key == "connman_manager_technologies":
            self.handle_technologies(value)

    def handle_services(self, services):
        # remove all services which disappeared
        for path in self._services.keys():
            if path not in services:
                logging.debug("remove service %s" % (path))
                self.emit("remove-service", self._services[path])
                del self._services[path]

        # now add all new services
        for path in services:
            if path not in self._services.keys():
                logging.debug("add service %s" % (path))
                self._services[path] = connman.service.Service(self._bus, path)
                self.emit("add-service", self._services[path])

    def handle_technologies(self, technologies):
        # remove all technologies which disappeared
        for path in self._technologies.keys():
            if path not in technologies:
                logging.debug("remove technology %s" % (path))
                self.emit("remove-technology", self._technologies[path])
                del self._technologies[path]

        # now add all new technologies
        for path in technologies:
            if path not in self._technologies.keys():
                logging.debug("add technology %s" % (path))
                self._technologies[path] = connman.technology.Technology(self._bus, path)
                self.emit("add-technology", self._technologies[path])

    @property
    def uid(self):
        return self._uid

    @property
    def attributes(self):
        return self._attr

    #############################################################################

    def GetState(self):
        self.get_interface("org.moblin.connman.Manager").GetState()

    def CreateProfile(self, name):
        self.get_interface("org.moblin.connman.Manager").CreateProfile(name)

    def RemoveProfile(self, path):
        self.get_interface("org.moblin.connman.Manager").RemoveProfile(path)

    def RequestScan(self, type):
        self.get_interface("org.moblin.connman.Manager").RequestScan(type)

    def EnableTechnology(self, type):
        self.get_interface("org.moblin.connman.Manager").EnableTechnology(type)

    def DisableTechnology(self, type):
        self.get_interface("org.moblin.connman.Manager").DisableTechnology(type)

    def GetServices(self):
        self.get_interface("org.moblin.connman.Manager").GetServices()

    def LookupService(self, pattern):
        self.get_interface("org.moblin.connman.Manager").LookupService(pattern)

    def ConnectService(self, network):
        self.get_interface("org.moblin.connman.Manager").ConnectService(network)
                
    def RegisterAgent(self, path):
        self.get_interface("org.moblin.connman.Manager").RegisterAgent(path)
        
    def RegisterCounter(self, path, interval):
        self.get_interface("org.moblin.connman.Manager").RegisterCounter(path, interval)

    def UnregisterCounter(self, path):
        self.get_interface("org.moblin.connman.Manager").UnregisterCounter(path, interval)

    def RequestSession(self):
        self.get_interface("org.moblin.connman.Manager").RequestSession()

    @property
    def State(self):
        return self._attr["State"]

    @property
    def AvailableTechnologies(self):
        return self._attr["AvailableTechnologies"]
    
    @property
    def EnabledTechnologies(self):
        return self._attr["EnabledTechnologies"]

    @property
    def ConnectedTechnologies(self):
        return self._attr["ConnectedTechnologies"]

    @property
    def DefaultTechnology(self):
        return self._attr["DefaultTechnologies"]

    @property
    def OfflineMode(self):
        return self._attr["OfflineMode"]

    @OfflineMode.setter
    def OfflineMode(self, mode):
        self.get_interface("org.moblin.connman.Manager").SetProperty("OfflineMode", mode)

    @property
    def ActiveProfile(self):
        return self._attr["ActiveProvfle"]

    @ActiveProfile.setter
    def OfflineMode(self, profile):
        self.get_interface("org.moblin.connman.Manager").SetProperty("ActiveProfile", profile)

    @property
    def Profiles(self):
        return self._attr["Proviles"]

    @property
    def Technologies(self):
        return self._attr["Technologies"]

    @property
    def Networks(self):
        return self._attr["Networks"]
