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

class Manager(dbus_object.dbus_object):
    def __init__(self, bus, uid):
        dbus_object.dbus_object.__init__(self, bus, "org.genivi.gcm", uid, "gcm_manager")

        self._attr = collections.defaultdict(lambda: "<missing>")
        self.register_interface("org.genivi.gcm.Manager", self._attr)

        self.update_properties()

    @property
    def uid(self):
        return self._uid

    @property
    def attributes(self):
        return self._attr

    #############################################################################

    def CreateGcmService(self, id):
        return self.get_interface("org.genivi.gcm.Manager").CreateGcmService(id)

    def DestroyGcmService(self, path):
        self.get_interface("org.genivi.gcm.Manager").DestroyGcmService(path)

    def Reset(self):
        self.get_interface("org.genivi.gcm.Manager").Reset()

    @property
    def Foo(self):
        return self._attr["Foo"]

