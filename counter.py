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

import dbus
import dbus.service

import logging
import traceback

class CounterStats(object):
    def __init__(self, ifname, rx_bytes = 0, tx_bytes = 0):
        logging.debug("ifname %s, rx_bytes %d, tx_bytes %d" % (ifname, rx_bytes, tx_bytes))
        self.ifname = ifname
        self._rx_bytes = rx_bytes
        self._tx_bytes = tx_bytes

    def __repr__(self):
        return "<CounterStats: %s, rx %d, tx %d>" % (self.ifname, self._rx_bytes, self._tx_bytes)

    @property
    def interface(self):
        return self.ifname

    @property
    def RX_Bytes(self):
        return self._rx_bytes

    @RX_Bytes.setter
    def RX_Bytes(self, rx_bytes):
        self._rx_bytes = rx_bytes

    @property
    def TX_Bytes(self):
        return self._tx_bytes

    @TX_Bytes.setter
    def TX_Bytes(self, tx_bytes):
        self._tx_bytes = tx_bytes


class Counter(dbus.service.Object):
    def __init__(self, manager, bus, object_path):
        dbus.service.Object.__init__(self, bus, object_path)
        self.manager = manager
        self.ifs = {}

    @dbus.service.method("org.moblin.connman.Counter",
                         in_signature='', out_signature='')
    def Release(self):
        logging.debug("release counter object")
        self.ifs = {}

    @dbus.service.method("org.moblin.connman.Counter",
                         in_signature='a{sv}', out_signature='')
    def Usage(self, stats):
        try:
            name = str(stats["Interface"])
            RX_Bytes = int(stats["RX.Bytes"])
            TX_Bytes = int(stats["TX.Bytes"])

            if name not in self.ifs:
                self.ifs[name] = CounterStats(name, RX_Bytes, TX_Bytes)
            else:
                self.ifs[name].RX_Bytes = RX_Bytes
                self.ifs[name].TX_Bytes = TX_Bytes
            
                self.manager.send_update(self.ifs[name])
        except:
            traceback.print_exc()

class CounterManager(gobject.GObject):
    __gsignals__ = {
        "counter-update": (gobject.SIGNAL_RUN_FIRST,
                           gobject.TYPE_NONE,
                           (object,)),
        }

    def __init__(self, bus, object_path):
        gobject.GObject.__init__(self)
        self.counter = Counter(self, bus, object_path)

    def send_update(self, stats):
        logging.debug("emit counter-update %s" % (stats))
        self.emit("counter-update", stats)

        
