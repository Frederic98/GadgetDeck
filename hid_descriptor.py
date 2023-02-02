#!/usr/bin/env python3
import argparse
import pathlib
import re
import sys
from typing import Union, TextIO

import hid_parser


def parse_descriptor(file: Union[str, TextIO]) -> list[int]:
    if isinstance(file, (str, pathlib.Path)):
        # If a path to a file was specified, call this function with the opened file
        with open(file, 'rt') as f:
            return parse_descriptor(f)
    else:
        report = []
        for line in file:
            # Strip comments
            if '//' in line:
                line, comment = line.split('//', 1)
            line = line.strip()
            # Get all 0x.. values
            for byte in re.finditer(r'0x([0-9A-Fa-f]{2})', line):
                report.append(int(byte.group(1), 16))
        return report


def get_input_size(descriptor: list[int]) -> int:
    try:
        return hid_parser.ReportDescriptor(descriptor).get_input_report_size().byte
    except:
        return 0

def get_output_size(descriptor: list[int]) -> int:
    try:
        return hid_parser.ReportDescriptor(descriptor).get_output_report_size().byte
    except:
        return 0

def get_feature_size(descriptor: list[int]) -> int:
    try:
        return hid_parser.ReportDescriptor(descriptor).get_feature_report_size().byte
    except:
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Parse HID Descriptor')
    action = parser.add_mutually_exclusive_group()
    action.add_argument('-x', '--hex', action='store_const', const='x', dest='action', help='Get the bytes of the HID report descriptor in HEX format')
    action.add_argument('-i', '--input_size', action='store_const', const='i', dest='action', help='Calculate the HID input report size')
    action.add_argument('-o', '--output_size', action='store_const', const='o', dest='action', help='Calculate the HID output report size')
    action.add_argument('-f', '--feature_size', action='store_const', const='f', dest='action', help='Calculate the HID feature report size')
    parser.add_argument('filename')
    parser.set_defaults(action='x')
    args = parser.parse_args()

    report = parse_descriptor(args.filename)
    if args.action == 'x':
        output = ''.join(f'{b:>02X}' for b in report)
    elif args.action == 'i':
        output = str(get_input_size(report))
    elif args.action == 'o':
        output = str(get_output_size(report))
    elif args.action == 'f':
        output = str(get_feature_size(report))
    else:
        # SHOULD be unreachable
        sys.exit()

    sys.stdout.write(output)
    sys.stdout.flush()
    sys.exit(0)

    # # ToDo: add argument to calculate input report size
    # if len(sys.argv) < 2:
    #     sys.stderr.write('ERROR: No HID report descriptor file specified')
    #     exit(1)
    # filename = sys.argv[1]
    # hex_string = ''.join(f'{b:>02X}' for b in parse_descriptor(filename))
    # sys.stdout.write(hex_string)
    # sys.stdout.flush()
    # exit(0)
