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

class PrimaryDataContext(dbus_object.dbus_object):
    def __init__(self, bus, uid):
        dbus_object.dbus_object.__init__(self, bus, "org.ofono", uid, "ofono_primarycontext")

        self._attr = collections.defaultdict(lambda: "<missing>")

        self.register_interface("org.ofono.PrimaryDataContext", self._attr)
        self.update_properties()

    @property
    def uid(self):
        return self._uid

    @property
    def attributes(self):
        return self._attr

    #############################################################################

    @property
    def Active(self):
        return self._attr["Active"]

    @property
    def AccessPointName(self):
        return self._attr["AccessPointName"]

    @property
    def Type(self):
        return self._attr["Type"]

    @property
    def Username(self):
        return self._attr["Username"]

    @property
    def Password(self):
        return self._attr["Password"]

    @property
    def Name(self):
        return self._attr["Name"]

    @property
    def Settings(self):
        return self._attr["Settings"]
