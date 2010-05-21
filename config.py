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

import os
import logging

import collections
import xml.dom.minidom

class config_wrapper:
    def __init__(self, attr):
        self._attr = attr

    def __repr__(self):
        return "<config %s>" % self.name

    @property
    def name(self):
        return self._attr["name"]

    @property
    def id(self):
        return self._attr["id"][0]

    @property
    def type(self):
        return self._attr["type"][0]

    @property
    def pin(self):
        return self._attr["pin"][0]

    @property
    def apn(self):
        return self._attr["apn"][0]

    @property
    def ssid(self):
        return self._attr["ssid"][0]

    @property
    def passphrase(self):
        return self._attr["passphrase"][0]

class application_wrapper:
    def __init__(self, attr):
        self._attr = attr

    def __repr__(self):
        return "<application %s>" % self.name

    @property
    def name(self):
        return self._attr["name"]

    @property
    def id(self):
        return int(self._attr["id"][0])

    @property
    def priority(self):
        return self._attr["priority"][0]

class device_wrapper:
    def __init__(self, attr):
        self._attr = attr

    def __repr__(self):
        return "<device %s>" % self.name

    @property
    def name(self):
        return self._attr["name"]

    @property
    def priority(self):
        return self._attr["priority"]


class config_parser:
    def __init__(self):
        self.configs = None
        self.applications = None
        self.devices = None

    def _get_text(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + str(node.data)
        return rc

    def _get_elements(self, nodes):
        d = collections.defaultdict(lambda: [None])
        for node in nodes:
            if node.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
                key = str(node.tagName)
                value = str(self._get_text(node.childNodes))
                if key in d:
                    d[key].append(value)
                else:
                    d[key] = [ value ]
        return d

    def _parse_type(self, doc, name, wrapper):
        l = []
        nodes = doc.getElementsByTagName(name)
        for node in nodes:
            d = self._get_elements(node.childNodes)
            d["name"] = str(node.getAttribute("name"))
            l.append(wrapper(d))
        return l

    def _handle_gcm(self, gcm):
        self.configs = self._parse_type(gcm, "config", config_wrapper)
        self.applications = self._parse_type(gcm, "application", application_wrapper)
        self.devices = self._parse_type(gcm, "device", device_wrapper)

    def read_xml(self, file):
        dom = xml.dom.minidom.parse(file)
        self._handle_gcm(dom)

def get_parser():
    search_paths = [ ".", "./connman", "./gcm/connman" ]
    for sp in search_paths:
        file_path = os.path.abspath(os.path.join(sp, "config.xml"))
        if os.path.exists(file_path):
            parser = config_parser()
            parser.read_xml(file_path)
            return parser

    return None

##########################################################
# XXX do some cleanup here, it is not necessary to parse
# and iterate that much...

map = { "high" : 0,
        "default": 1,
        "low": 2, }

def get_application(id):
    parser = get_parser()
    for app in parser.applications:
        if id == app.id:
            return app

    return None

def id2devtypes(id):
    """Returns the list of device classes which are allowed to use by the application.
    The list is ordered by cost"""
    devtypes = []

    parser = get_parser()
    app = get_application(id)
    if app != None:
        for dev in parser.devices:
            if app.priority in dev.priority:
                devtypes.append(dev.name)

    return devtypes

def id2configurations(id):
    """Returns a dict of configurations for given application id.
    Note that only configurations are returned which are allowed to
    be used by the application."""
    services = {}
    parser = get_parser()

    devtypes = id2devtypes(id)

    for config in parser.configs:
        if config.type in devtypes:
            services[config.name] = config

    return services

def get_config(name):
    parser = get_parser()

    for config in parser.configs:
        if name == config.name:
            return config

    return None

if __name__ == "__main__":
    import pprint
    print "Services for id 0"
    pprint.pprint(id2configurations(0))
    print "\nServices for id 1"
    pprint.pprint(id2configurations(1))

    print "\nID to device class for 0:"
    print id2devtypes(0)
    print "\nID to device class for 1:"
    print id2devtypes(1)

    print "\nget_config(\"Router1\")"
    print get_config("Router1")
