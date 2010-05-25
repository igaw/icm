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

import dbus
import dbus.service
import gobject

import pdb
import logging
import traceback

import icm_service

class Manager(dbus.service.Object):
    def __init__(self, wrapper, bus, object_path='/'):
        dbus.service.Object.__init__(self, bus, object_path)
        self.bus = bus
        self.wrapper = wrapper
        self.icm_services = {}

    @dbus.service.method("de.bmwcarit.icm.Manager", in_signature="", out_signature="a{sv}")
    def GetProperties(self):
        logging.debug("get properties")
        return { "Foo" : "Bar" }

    @dbus.service.signal("de.bmwcarit.icm.Manager", signature="sv")
    def PropertyChanged(self, key, value):
        logging.debug("sending property changed signal for %s %s" % (key, value))
        pass

    @dbus.service.method("de.bmwcarit.icm.Manager", in_signature="sv", out_signature="")
    def SetProperty(self, key, value):
        logging.debug("set property %s to %s" % (str(key), str(value)))
        pass

    @dbus.service.method("de.bmwcarit.icm.Manager", in_signature="i", out_signature="o",
                         sender_keyword="sender")
    def CreateIcmService(self, id, sender=None):
        logging.debug("create new service for sender %s" % sender)

        # No need to check permission if application is allowed to
        # access this fuction, because this should be configured by
        # policykit.  Note: policykit does not support dynamic updates
        # of the rule sets yet (see
        # http://www.freedesktop.org/wiki/Software/PolicyKit/PluggableArchitecture
        # ).

        uid = "/service/%d" % (id)
        if uid in self.icm_services:
            logging.debug("app with id %d has already requested a connnection" % id)
            return uid

        try:
            logging.debug("adding service %s to dbus" % uid)

            gsrv = icm_service.IcmServiceWrapper(self.bus, uid, id)
            self.wrapper.add_service(gsrv)
            gsrv._icm_service.add_to_connection(self.bus, uid)

            self.icm_services[uid] = gsrv

            return uid
        except:
            traceback.print_exc()
            raise

        raise LookupError

    @dbus.service.method("de.bmwcarit.icm.Manager", in_signature="o", out_signature="",
                         sender_keyword="sender")
    def DestroyIcmService(self, uid, sender=None):
        logging.debug("destroy service '%s' for sender %s" % (uid, sender))

        if uid not in self.icm_services:
            logging.debug("app with id %d has not requested a connection" % id)
            raise LookupError

        try:
            logging.debug("removing service %s from dbus" % uid)

            gsrv = self.icm_services.pop(uid)
            self.wrapper.remove_service(gsrv)
            gsrv._icm_service.remove_from_connection()

            gsrv = None
        except:
            traceback.print_exc()

    @dbus.service.method("de.bmwcarit.icm.Manager", in_signature="", out_signature="",
                         sender_keyword="sender")
    def Reset(self, sender=None):
        logging.debug("reset request from %s" % (sender))

        for id, icm_service in self.icm_services.items():
            try:
                icm_service.reset()
            except:
                pass
            icm_service._icm_service.remove_from_connection()
        self.icm_services = {}

        self.wrapper.reset()


class ManagerWrapper(gobject.GObject):
    __gsignals__ = {
        "add-service": (gobject.SIGNAL_RUN_FIRST,
                        gobject.TYPE_NONE,
                        (object,)),
        "remove-service": (gobject.SIGNAL_RUN_FIRST,
                           gobject.TYPE_NONE,
                           (object,)),
        "reset": (gobject.SIGNAL_RUN_FIRST,
                  gobject.TYPE_NONE,
                  ()),
        }
    def __init__(self, bus, object_path='/'):
        gobject.GObject.__init__(self)
        self._manager = Manager(self, bus, object_path)
        self.bus = bus
        self.icm_services = {}

    def update_state(self, text):
        logging.debug("update_state called");
        self._manager.connectionState(text)


    def add_service(self, service):
        self.emit("add-service", service)

    def remove_service(self, service):
        self.emit("remove-service", service)

    def reset(self):
        self.emit("reset")
