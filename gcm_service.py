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

import dbus
import dbus.service
import gobject

import logging
import traceback

class GcmService(dbus.service.Object):
    def __init__(self, app_id, sender):
        dbus.service.Object.__init__(self)
        self._state = "no service selected"
        self._app_id = app_id
        self._sender = sender
        self._RX_Bytes = 0
        self._TX_Bytes = 0
        self._name = ""

    # dbus interface
    @dbus.service.method("org.genivi.gcm.GcmService", in_signature="", out_signature="a{sv}")
    def GetProperties(self):
        logging.debug("get properties")
        return { "State" : self._state,
                 "RX.Bytes" : self._RX_Bytes,
                 "TX.Bytes" : self._TX_Bytes,
                 "Name": self._name}

    @dbus.service.signal("org.genivi.gcm.GcmService", signature="sv")
    def PropertyChanged(self, key, value):
        logging.debug("sending property changed signal for %s %s" % (key, value))

    @dbus.service.method("org.genivi.gcm.GcmService", in_signature="sv", out_signature="")
    def SetProperty(self, key, value):
        logging.debug("set property %s to %s" % (str(key), str(value)))
        if key == "State":
            self._state = str(value)

    @dbus.service.method("org.genivi.gcm.GcmService", in_signature="", out_signature="",
                         sender_keyword="sender")
    def ConnectionRequest(self, sender=None):
        logging.debug("connection request from %s" % sender)
        try:
            self._sender.request_connection(self._app_id)
        except:
            traceback.print_exc()

    @dbus.service.method("org.genivi.gcm.GcmService", in_signature="", out_signature="",
                         sender_keyword="sender")
    def ConnectionRelease(self, sender=None):
        logging.debug("connection release from %s" % sender)
        try:
            self._sender.release_connection(self._app_id)
            self._sender.set_connection_state("no service selected")
            self._sender.set_name("")
        except:
            traceback.print_exc()



class GcmServiceWrapper(gobject.GObject):
    __gsignals__ = {
        "request-connection": (gobject.SIGNAL_RUN_FIRST,
                               gobject.TYPE_NONE,
                               (object,)),
        "release-connection": (gobject.SIGNAL_RUN_FIRST,
                               gobject.TYPE_NONE,
                               (object,)),
        "reset": (gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ()),
        }

    def __init__(self, bus, uid, app_id):
        gobject.GObject.__init__(self)
        self.bus = bus
        self.uid = uid
        self._gcm_service = GcmService(app_id, self)
        self._interface_name = ""

    def request_connection(self, id):
        logging.debug("emit request-connection")
        self.emit("request-connection", id)

    def release_connection(self, id):
        logging.debug("emit release-connection")
        self.emit("release-connection", id)

    def service_property_changed(self, service, key, value):
        if key == "connman_service_state":
            self.set_connection_state(value)
        elif key == "connman_service_name":
            self.set_name(value)

    def set_connection_state(self, state):
        logging.debug("set connection state to %s" % state)
        self._gcm_service._state = state
        self._gcm_service.PropertyChanged("State", self._gcm_service._state)

    def handle_counter_update(self, manager, counter):
        if counter.interface == self._interface_name:
            self._gcm_service._TX_Bytes = counter.TX_Bytes
            self._gcm_service._RX_Bytes = counter.RX_Bytes
            self._gcm_service.PropertyChanged("TX.Bytes", self._gcm_service._TX_Bytes)
            self._gcm_service.PropertyChanged("RX.Bytes", self._gcm_service._RX_Bytes)

    def set_name(self, name):
        logging.debug("set service name to '%s'" % (name))
        self._gcm_service._name = name
        self._gcm_service.PropertyChanged("Name", self._gcm_service._name)

    def set_interface(self, interface_name):
        self._interface_name = interface_name

    def reset(self):
        logging.debug("emit reset")
        self.emit("reset", self._app_id)
        self.set_connection_state("no service selected")
