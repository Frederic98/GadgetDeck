#!/usr/bin/env python
import argparse
import glob
import subprocess
import os
from typing import Union

import hid_parser
import usb_gadget

gadget = usb_gadget.USBGadget('gadget-deck')


def gadget_setup():
    gadget.idVendor = '0x1d6b'
    gadget.idProduct = '0x0104'
    gadget.bcdDevice = '0x0100'
    gadget.bcdUSB = '0x0200'
    # gadget.bDeviceClass = '0x02'
    # gadget.bDeviceSubClass = '0x00'
    # gadget.bDeviceProtocol = '0x00'

    strings = gadget['strings']['0x409']
    strings.serialnumber = '0123456789'
    strings.manufacturer = 'Valve'
    strings.product = 'Steam Deck'

    config = gadget['configs']['c.1']
    config.bmAttributes = '0x80'
    config.MaxPower = '250'
    config['strings']['0x409'].configuration = 'Steam Deck Configuration'
    return config


def gadget_activate():
    gadget.activate()


def gadget_destroy():
    for config in os.scandir(gadget['configs'].path):
        config = usb_gadget.ConfigFS(config.path)
        for function in os.scandir(config.path):
            if function.is_symlink():
                os.remove(function.path)
        for language in os.scandir(config['strings'].path):
            os.rmdir(language.path)
        os.rmdir(config.path)
    for function in os.scandir(gadget['functions'].path):
        os.rmdir(function.path)
    for language in os.scandir(gadget['strings'].path):
        os.rmdir(language.path)
    os.rmdir(gadget.path)


def create_function_hid(name: str, report: Union[str, list[int]], protocol=0, subclass=0):
    if isinstance(report, str):
        with open(report, 'rt') as f:
            descriptor = hid_parser.ReportDescriptor.from_str(f.read())
    else:
        descriptor = hid_parser.ReportDescriptor(report)
    hid = usb_gadget.HIDFunction(gadget, name)
    hid.protocol = str(protocol)
    hid.subclass = str(subclass)
    hid.report_length = str(descriptor.get_input_report_size().byte)
    hid.report_desc = bytes(descriptor.data)
    gadget.link(hid, gadget['configs']['c.1'])
    return hid

def remove_function(name):
    os.unlink(gadget['configs']['c.1'][name].path)
    os.rmdir(gadget['functions'][name].path)

def function_enable(function: str, activate=True):
    gadget.deactivate()
    if function in ('joystick', 'mouse', 'keyboard'):
        function = create_function_hid(function, f'HID Descriptors/{function}.txt')
        if activate:
            gadget.activate()
        chmod_hidg()
    if function == 'mtp':
        function = usb_gadget.USBFunction(gadget, 'ffs.mtp')
        gadget.link(function, gadget['configs']['c.1'])
        os.mkdir('/dev/ffs-mtp')
        subprocess.call(['mount', '-t', 'functionfs', 'mtp', '/dev/ffs-mtp'])
        if activate:
            gadget.activate()
    if function == 'shell':
        function = usb_gadget.USBFunction(gadget, 'acm.shell')
        gadget.link(function, gadget['configs']['c.1'])
        if activate:
            gadget.activate()
        subprocess.call(['systemctl', 'start', f'getty@ttyGS{function.port_num}.service'])


def function_disable(function: str, activate=True):
    gadget.deactivate()
    if function in ('joystick', 'mouse', 'keyboard'):
        remove_function(f'hid.{function}')
    if function == 'mtp':
        subprocess.call(['umount', '/dev/ffs-mtp'])
        os.rmdir('/dev/ffs-mtp')
        remove_function('ffs.mtp')
    if function == 'shell':
        function = usb_gadget.USBFunction(gadget, 'acm.shell')
        subprocess.call(['systemctl', 'start', f'getty@ttyGS{function.port_num}.service'])
        remove_function('acm.shell')
    linked_functions = [f for f in os.scandir(gadget['configs']['c.1'].path) if f.is_symlink()]
    if activate and linked_functions:
        gadget.activate()
        chmod_hidg()

def chmod_hidg():
    for dev in glob.glob('/dev/hidg*'):
        subprocess.call(['chmod', '0666', dev])


if __name__ == '__main__':
    parser = argparse.ArgumentParser('steam-gadget')
    action_parser = parser.add_subparsers(title='action', required=True)

    action_setup = action_parser.add_parser('setup')
    action_setup.set_defaults(action=gadget_setup)

    action_destroy = action_parser.add_parser('destroy')
    action_destroy.set_defaults(action=gadget_destroy)

    action_activate = action_parser.add_parser('activate')
    action_activate.set_defaults(action=gadget_activate)

    action_enable = action_parser.add_parser('enable')
    action_enable.add_argument('function')
    action_enable.add_argument('--no-activate', action='store_false', dest='activate')
    action_enable.set_defaults(action=function_enable)

    action_disable = action_parser.add_parser('disable')
    action_disable.add_argument('function')
    action_disable.add_argument('--no-activate', action='store_false', dest='activate')
    action_disable.set_defaults(action=function_disable)

    args = vars(parser.parse_args())
    action = args.pop('action')
    action(**args)

# steam_gadget = usb_gadget.USBGadget('steam_gadget')
# config = gadget_setup(steam_gadget)
# joystick = function_hid(steam_gadget, 'joystick0', 'HID Descriptors/joystick.txt')
# keyboard = function_hid(steam_gadget, 'keyboard0', 'HID Descriptors/keyboard.txt')
# mouse = function_hid(steam_gadget, 'mouse0', 'HID Descriptors/mouse.txt')
# steam_gadget.link(joystick, config)
# steam_gadget.link(keyboard, config)
# steam_gadget.link(mouse, config)
# steam_gadget.activate()
