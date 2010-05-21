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

import gobject
import traceback
import logging
import dbus

import gcm.gcm_service
import gcm.manager

class app_base(gobject.GObject):
    def __init__(self, id, stats):
        gobject.GObject.__init__(self)
        self._id = id
        self._stats = stats
        self._bus = dbus.SystemBus()
        self.hid = None

        # gcm dbus objects
        self._gcm_manager = None
        self._gcm_service_path = None
        self._gcm_service = None

        try:
            self._bus.watch_name_owner('org.genivi.gcm', self.gcm_name_owner_changed)
        except dbus.DBusException:
            traceback.print_exc()
            exit(1)

    def gcm_name_owner_changed(self, proxy):
        try:
            logging.debug(str(proxy))

            if proxy:
                self._gcm_manager = gcm.manager.Manager(self._bus, "/")
            else:
                self._gcm_manager = None
                self._gcm_service = None
                self._gcm_service_path = None

        except dbus.DBusException:
            traceback.print_exc()
            exit(1)

    def connection_request(self):
        if self._gcm_manager != None and self._gcm_service_path == None:
            self._gcm_service_path = self._gcm_manager.CreateGcmService(self._id)

        if self._gcm_service_path != None and self._gcm_service == None:
            logging.debug("add gcm service object proxy %s" % (self._gcm_service_path))
            self._gcm_service = gcm.gcm_service.GcmService(self._bus, self._gcm_service_path)

            self.hid = self._gcm_service.connect("property-changed", self.property_changed)

        self._gcm_service.ConnectionRequest()

    def connection_release(self):
        if self._gcm_service:
            logging.debug("release connection")
            self._gcm_service.ConnectionRelease()

        
    def cleanup(self):
            logging.debug("remove gcm service object proxy %s" % (self._gcm_service_path))
            self._gcm_service.Disconnect(self.hid)
            
            self._gcm_manager.DestroyGcmService(self._gcm_service_path)

    def start(self):
        pass

    def property_changed(self, service, key, value):
        if key == "gcm_gcm_service_state":
            self._handle_state(value)
        elif key == "gcm_gcm_service_name":
            self._handle_name(value)

    def _handle_state(self, state):
        logging.debug("state changed for %s to '%s'" % (self._gcm_service_path, state))
        self._stats.set_state(state)

        if state in ["ready", "online"]:
            self.online()
        else:
            self.offline()

    def online(self):
        pass

    def offline(self):
        pass


    def _handle_name(self, name):
        self._stats.set_name(name)
