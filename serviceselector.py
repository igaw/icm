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

import sort
import logging
import config

class ServiceSelector:
    def __init__(self, configs, devtypes, services, modems):
        self._configs = configs
        self._devtypes = devtypes
        self._services = services
        self._modems = modems
        self._sorter = [ sort.sorter_strength, 
                         sort.sorter_type, 
                         sort.sorter_wifi_security, 
                         sort.sorter_ethernet_index ]

    def sort(self):
        for s in self._sorter:
            s(self._services)

    def filter(self):
        logging.debug("filter out all service type which are not %s" % (self._devtypes))
        self._services = [x for x in self._services if x.Type in self._devtypes]

    def select(self):
        self.filter()
        self.sort()

        logging.debug("available services (sorted)")
        for s in self._services:
            logging.debug(s)

        # Are we already connected to one in our list? If yes
        # we just take that one.
        for s in self._services:
            if s.State in ["ready", "online"]:
                return (config.get_config(s.Name), s)

        # We have to establish a new connection, therefore
        # we need to select first one.
        for s in self._services:
            if s.Type == "ethernet":
                # XXX ethernet is handled differently by connman!? See
                # Connect() in service.api.txt
                return (None, s)
            elif s.Type == "wifi":
                if s.Security != "none":
                    if s.Name in self._configs:
                        return (self._configs[s.Name], s)
                else:
                    return (None, s)
            elif s.Type == "cellular":
                # Let's pick the first one

                # XXX ugly hack ahead...
                tmp = s.uid.split("/")[-1]
                tmp = tmp.split("_")
                imsi = tmp[1]

                modem = None
                for m in self._modems:
                    if m.SubscriberIdentity == imsi:
                        modem = m
                        break
                if modem:
                    name = "%s %s" % (modem.Model, modem.Serial)
                    if name in self._configs:
                        return (self._configs[name], s)

        return (None, None)
