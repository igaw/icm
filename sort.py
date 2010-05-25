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

# Note that the sort has to be stable

def sorter_strength(data):
    data.sort(lambda x,y: -cmp(x.Strength, y.Strength))

def sorter_type(data):
    def cmp_type(a, b):
        prio_map = { 'wifi': 1,
                     'ethernet' : 0,
                     'cellular' : 2 }
        p_a = prio_map[a.Type]
        p_b = prio_map[b.Type]
        return p_a - p_b

    data.sort(cmp_type)

def sorter_wifi_security(data):
    def cmp_wifi_security(a, b):
        if a.Type != "wifi" or b.Type != "wifi":
            return 0

        prio_map = { "none" : 2,
                     "wep" : 1,
                     "psk" : 0,
                     "ieee8021x" : 0,
                     "wpa" : 0,
                     "rsn" : 0 }

        p_a = prio_map[a.Security]
        p_b = prio_map[b.Security]
        return p_a - p_b

    data.sort(cmp_wifi_security)

def sorter_ethernet_index(data):
    def cmp_ethernet_index(a, b):
        if a.Type != "ethernet" or b.Type != "ethernet":
            return 0

        i_a = int(a.Ethernet_Interface[3:])
        i_b = int(b.Ethernet_Interface[3:])
        return i_a - i_b

    data.sort(cmp_ethernet_index)
