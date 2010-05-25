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
import gobject
import logging
import traceback

import ofono.manager
import connman.manager

import appreq
import config
import serviceselector
import counter

class ICM(gobject.GObject):
    def __init__(self, bus, icm_manager):
        gobject.GObject.__init__(self)

        self.bus = bus
        self._icm_manager = icm_manager

        self.hid = {}

        self._icm_manager.connect("add-service", self.icm_manager_add_service)
        self._icm_manager.connect("remove-service", self.icm_manager_remove_service)
        self._icm_manager.connect("reset", self.reset)

        # connman dbus objects
        self.connman_manager = None

        # ofono dbus objects
        self.ofono_manager = None

        # connection requests
        self.appreq = {}

        try:
            self.bus.watch_name_owner('org.moblin.connman', self.connman_name_owner_changed)
            self.bus.watch_name_owner('org.ofono', self.ofono_name_owner_changed)

        except dbus.DBusException:
            traceback.print_exc()
            exit(1)

        self.counter_path = "/counter"
        self.counter = counter.CounterManager(self.bus, self.counter_path)

    def _connect(self, object, signal, cb):
        if object not in self.hid:
            self.hid[object] = {}

        hid = object.connect(signal, cb)
        self.hid[object][signal] = hid

    def _disconnect(self, object, signal):
        object.disconnect(self.hid[object][signal])
        del self.hid[object][signal]

        if len(self.hid[object]) == 0:
            del self.hid[object]


    def connman_name_owner_changed(self, proxy):
        try:
            logging.debug(str(proxy))

            if proxy:
                self.connman_manager = connman.manager.Manager(self.bus, "/")

                self._connect(self.connman_manager, "add-service", self.add_service)
                self._connect(self.connman_manager, "remove-service", self.remove_service)
                self._connect(self.connman_manager, "add-technology", self.add_technology)
                self._connect(self.connman_manager, "remove-technology", self.remove_technology)

                for srv in self.connman_manager.get_services():
                    self.add_service(self.connman_manager, srv)
                for tch in self.connman_manager.get_technologies():
                    self.add_technology(self.connman_manager, tch)

                self.connman_manager.RegisterCounter(self.counter_path, 2) # poll all 2 seconds
            else:
                if self.connman_manager:
                    self._disconnect(self.connman_manager, "add-service")
                    self._disconnect(self.connman_manager, "remove-service")
                self.connman_manager = None

        except dbus.DBusException:
            traceback.print_exc()
            exit(1)

    def ofono_name_owner_changed(self, proxy):
        try:
            logging.debug(str(proxy))

            if proxy:
                self.ofono_manager = ofono.manager.Manager(self.bus, "/")

                self._connect(self.ofono_manager, "add-modem", self.add_modem)
                self._connect(self.ofono_manager, "remove-modem", self.remove_modem)

                for modem in self.ofono_manager.get_modems():
                    self.add_modem(self.ofono_manager, modem)
            else:
                if self.ofono_manager:
                    self._disconnect(self.ofono_manager, "add-modem")
                    self._disconnect(self.ofono_manager, "remove-modem")
                self.ofono_manager = None

        except dbus.DBusException:
            traceback.print_exc()
            exit(1)

    def icm_manager_add_service(self, manager, service):
        self._connect(service, "request-connection", self.add_app_id)
        self._connect(service, "release-connection", self.rem_app_id)

    def icm_manager_remove_service(self, manager, service):
        self._disconnect(service, "request-connection")
        self._disconnect(service, "release-connection")

    def add_service(self, manager, service):
        logging.debug("add service %s" % (service.Name))

    def remove_service(self, manager, service):
        logging.debug("remove service %s" % (service.Name))

    def add_technology(self, manager, technology):
        logging.debug("technology %s state: %s" % (technology.Name, technology.State))

    def remove_technology(self, manager, technology):
        logging.debug("technology %s state: %s" % (technology.Name, technology.State))

    def add_modem(self, manager, modem):
        logging.debug("add modem %s" % modem.uid)
        self._connect(modem, "property-changed", self.modem_property_changed)

        self.handle_modem_powered(modem, modem.Powered)
        if modem.Powered:
            self.handle_modem_pin_required(modem, modem.PinRequired)

    def remove_modem(self, manager, modem):
        logging.debug("remove modem %s" % modem.uid)
        self._disconnect(modem, "property-changed")

    def modem_property_changed(self, modem, key, value):
        if key == "ofono_modem_powered":
            self.handle_modem_powered(modem, value)

        # We can not rely on the order of arrival of the signals, e.g:
        #   - Model (org.ofono.Manager)
        #   - PinRequired (org.ofono.SimManager)
        #   - Revision (org.ofono.Manager)
        #   - Serial (org.ofono.Manager)
        elif key == "ofono_modem_pinrequired" and modem.Model != "<missing>" and modem.Serial != "<missing>":
            self.handle_modem_pin_required(modem, value)
        elif key == "ofono_modem_serial":
            if modem.PinRequired != "none" and modem.Model != "<missing>":
                self.handle_modem_pin_required(modem, modem.PinRequired)
        elif key == "ofonoe_modem_model":
            if modem.PinRequired != "none" and modem.Serial != "<missing>":
                self.handle_modem_pin_required(modem, modem.PinRequired)
            

    def handle_modem_powered(self, modem, powered):
        if powered == 0:
            logging.debug("Power up modem %s", modem)

            try:
                modem.Powered = True
            except dbus.DBusException as e:
                # XXX Is this a bug in icm or ofono?
                logging.warning("Could not power up modem %s. Try again in 100 ms (%s)" % (modem, e))

    def handle_modem_pin_required(self, modem, pinrequired):
        if pinrequired == "pin":

            #import pdb
            #pdb.set_trace()

            # XXX We need a way to identify the SIM. EF_ICCID would be
            # the right choice if the hardware would work according
            # the spec...
            # For the time beeing use a simple workaround
            name = "%s %s" % (modem.Model, modem.Serial)
            logging.debug("%s (%s) needs '%s'" % (modem.uid, name, pinrequired))
            cfg = config.get_config(name)
            if cfg:
                try:
                    modem.EnterPin("pin", cfg.pin)
                except dbus.DBusException:
                    # XXX Is this a bug in icm or ofono?
                    logging.warning("Could not enter pin")
            else:
                logging.debug("no config found for '%s'" % (modem.uid))

    def get_services(self):
        return self.services.values()

    def add_app_id(self, icm_service, id):
        logging.debug("add_app_id: %s" % (id))

        cfgs = config.id2configurations(id)
        devtypes = config.id2devtypes(id)

        services = []
        modems = []

        if self.connman_manager != None and self.connman_manager._services != None:
            services = self.connman_manager._services.values()
        if self.ofono_manager != None and self.ofono_manager._modems != None:
            modems = self.ofono_manager._modems.values()

        selector = serviceselector.ServiceSelector(cfgs, devtypes, services, modems)
        (cfg, service) = selector.select()


        if service == None:
            logging.debug("no service selected")
            # XXX some retry logic is needed. Let's leave that for later
        else:
            logging.debug("selected services %s" % (service))
            logging.debug("service is in state %s" % (service.State))
            
            hid = service.connect("property-changed", icm_service.service_property_changed)
            self.hid[icm_service]["property-changed"] = hid

            hid = self.counter.connect("counter-update", icm_service.handle_counter_update)
            self.hid[icm_service]["counter-update"] = hid

            icm_service.set_connection_state(service.State)
            icm_service.set_name(service.Name)
            icm_service.set_interface(service.Ethernet_Interface)

        if service != None and service.State in ["idle", "failure"]:
            logging.debug("tell connamn to connect to service '%s'" % (service))

            if cfg != None:
                if cfg.apn:
                    cfg.APN = cfg.apn
                if cfg.passphrase:
                    service.Passphrase = cfg.passphrase

            service.srv_connect()

        req = appreq.AppReq(id)
        req.config = cfg
        req.service = service
        self.appreq[id] = req

        return self.appreq[id]

    def rem_app_id(self, icm_service, id):
        logging.debug("rem_app_id: %s" % (id))

        service = self.appreq[id].service

        if service != None and service.State in ["association", "configuration", "ready", "online" ]:
            logging.debug("tell connamn to disconnect from service '%s'" % (service))

            service.srv_disconnect()

        service.disconnect(self.hid[icm_service]["counter-update"])
        service.disconnect(self.hid[icm_service]["property-changed"])

        del self.appreq[id]

    def reset(self, object):
        logging.debug("reset icm")

        for id, appreq in self.appreq.items():
            logging.debug("reset id %s" % (id))

            try:
                appreq._service.srv_disconnect()
            except:
                pass

        self.appreq = {}

        for uid, service in self.connman_manager._services.items():
            try:
                service.srv_disconnect()
            except:
                pass
