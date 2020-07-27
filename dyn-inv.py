#!/usr/bin/env python

import argparse
import sys
import libvirt
import json
import socket
import subprocess, re
from ansible.module_utils._text import to_text


class ExampleInventory(object):
    def __init__(self):
        self.inventory = {}
        self.read_cli_args()
        self.boxes = self.list_boxes()
        if self.args.list:
            self.inventory = self.build_inventory()
        elif self.args.host:
            self.inventory = self.empty_inventory()
        else:
            self.inventory = self.empty_inventory()
        print(json.dumps(self.inventory, indent=2))

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

    @staticmethod
    def list_boxes():
        output = to_text(subprocess.check_output(["vagrant", "status"]), errors='surrogate_or_strict').split('\n')
        boxes = []
        for line in output:
            matcher = re.search(r"([^\s]+)[\s]+running \(.+", line)
            if matcher:
                boxes.append(matcher.group(1))
        return boxes

    def read_vagrantfile(self):
        if not self.vagrantfile:
            with open('Vagrantfile') as f:
                self.vagrantfile = f.read()
        return self.vagrantfile

    def get_network(self):
        m = re.search(r"private_network.*(192\.168\.\d+\.\d+)", self.read_vagrantfile())
        if not m:
            return None
        ip_addr = m.group(1)
        octets = ip_addr.split('.')
        octets[3] = '0'
        net_addr = '.'.join(octets)
        return net_addr

    def get_boxen_from_vagrantfile(self):
        "config.vm.define"

    @staticmethod
    def get_value(key, text):
        m = re.search(r"\s*" + key + r" (.*)\n", text)
        if m:
            return m.group(1).strip()

    def get_hostvars(self):
        vars = {}
        for box_name in self.boxes:
            output = to_text(subprocess.check_output(["vagrant", "ssh-config", box_name]), errors='surrogate_or_strict')

            identity_file = self.get_value("IdentityFile", output)
            ip = self.get_value("HostName", output)
            user = self.get_value("User", output)
            port = self.get_value("Port", output)
            # hostname = cls.get_value("Host", output)
            vars[box_name] = {
                'ansible_host': ip,
                'ansible_user': user,
                'ansible_ssh_private_key_file': identity_file,
                'ansible_ssh_port': port,
            }
        return vars

    def build_inventory(self):
        inv = self.empty_inventory()
        inv['_meta']['hostvars'] = self.get_hostvars()
        inv["all"] = { "children": [ "machines", "ungrouped" ] }
        inv["machines"] = { "hosts": self.boxes }
        return inv

ExampleInventory()

