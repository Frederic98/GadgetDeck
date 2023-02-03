#!/usr/bin/python3
import re
import math
import struct
from typing import BinaryIO, Union


class HIDGadget:
    def __init__(self, device: str, auto_update=False):
        self.device: BinaryIO = open(device, 'wb+')
        self.auto_update = auto_update

    def reset(self):
        pass

    def to_bytes(self) -> bytes:
        raise NotImplementedError

    def close(self):
        """Close HID interface"""
        self.reset()
        self.update()
        self.device.close()

    def update(self):
        self.device.write(self.to_bytes())
        self.device.flush()

    @staticmethod
    def remap(value, in_min, in_max, out_min, out_max, constrain=True):
        """Remap a value from in_min...in_max to out_min...out_max"""
        value = float(value - in_min) / float(in_max - in_min)          # Normalize value (0...1)
        value = (value * (out_max - out_min)) + out_min                 # Scale to out range
        if constrain:
            if out_min < out_max:
                value = max(out_min, min(value, out_max))
            else:
                # If the out range is reversed - out_min > out_max
                value = max(out_max, min(value, out_min))
        return value


class JoystickGadget(HIDGadget):
    def __init__(self, device, js_count, trig_count, btn_count, auto_update=False):
        HIDGadget.__init__(self, device, auto_update)
        btn_bytes = math.ceil(btn_count / 8)

        self.joysticks = [[0,0] for _ in range(js_count)]
        self.triggers = [0 for _ in range(trig_count)]
        self.buttons = [0 for _ in range(btn_bytes)]
        self.struct = struct.Struct('<' + 'b'*(js_count*2) + 'b'*trig_count + 'B'*btn_bytes)

    def set_joystick(self, i: int, x: float, y: float):
        self.joysticks[i][0] = int(self.remap(x, -1, 1, -127, 127))
        self.joysticks[i][1] = int(self.remap(y, -1, 1, -127, 127))
        if self.auto_update:
            self.update()

    def set_trigger(self, i: int, v: float):
        self.triggers[i] = int(self.remap(v, 0, 1, 0, 127))
        if self.auto_update:
            self.update()

    def set_button(self, i: int, v: bool):
        if v:
            self.buttons[i//8] |= (1 << (i%8))
        else:
            self.buttons[i//8] &= ~(1 << (i%8))
        if self.auto_update:
            self.update()

    def to_bytes(self):
        js = [value for joystick in self.joysticks for value in joystick]
        return self.struct.pack(*js, *self.triggers, *self.buttons)

    def reset(self):
        for i,joystick in enumerate(self.joysticks):
            self.joysticks[i][0] = 0
            self.joysticks[i][1] = 0
        for i,trigger in enumerate(self.triggers):
            self.triggers[i] = 0
        for i,button in enumerate(self.buttons):
            self.buttons[i] = 0

    def __repr__(self):
        js = " ".join([f"({x} {y})" for x,y in self.joysticks])
        trig = " ".join(str(v) for v in self.triggers)
        btn = " ".join(f"{v:>08b}" for v in self.buttons)
        return f'<{self.__class__.__qualname__} {js} - {trig} - {btn}>'


class MouseGadget(HIDGadget):
    def __init__(self, device, resolution=1, buttons=2, wheels=1, auto_update=False):
        HIDGadget.__init__(self, device, auto_update)
        self.xy_resolution = resolution
        btn_bytes = math.ceil(buttons / 8)

        self.x = 0
        self.y = 0
        self.buttons = [0 for _ in range(btn_bytes)]
        self.wheels = [0 for _ in range(wheels)]

    def to_bytes(self) -> bytes:
        buttons = b''.join(b.to_bytes(1, 'little') for b in self.buttons)
        x = self.x.to_bytes(self.xy_resolution, 'little', signed=True)
        y = self.y.to_bytes(self.xy_resolution, 'little', signed=True)
        wheels = b''.join(b.to_bytes(1, 'little') for b in self.wheels)
        return buttons + x + y + wheels

    def update(self):
        HIDGadget.update(self)
        self.x = 0
        self.y = 0
        for i,wheel in enumerate(self.wheels):
            self.wheels[i] = 0

    def reset(self):
        self.x = 0
        self.y = 0
        for i, btn in enumerate(self.buttons):
            self.buttons[i] = 0
        for i, wheel in enumerate(self.wheels):
            self.wheels[i] = 0

    def move(self, x, y):
        self.x = int(x)
        self.y = int(y)
        if self.auto_update:
            self.update()

    def set_button(self, i: int, v: bool):
        if v:
            self.buttons[i//8] |= (1 << (i%8))
        else:
            self.buttons[i//8] &= ~(1 << (i%8))
        if self.auto_update:
            self.update()


class KeyboardScanCode:
    __SYMBOLS = {'-': 0x2D, '=': 0x2E, '[': 0x2F, ']': 0x30, '\\': 0x31, ';': 0x33, '\'': 0x34, '`': 0x35, ',': 0x36, '.': 0x37, '/': 0x38}
    NULL = 0x00
    ERR_ROLLOVER = 0x01
    ERR_POSTFAIL = 0x02
    ERR_UNDEFINED = 0x03

    RETURN = ENTER = 0x28
    ESCAPE = 0x29
    BACKSPACE = 0x2A
    TAB = 0x2B
    SPACEBAR = SPACE = 0x2C
    CAPSLOCK = 0x39

    PRINTSCREEN = 0x46
    SCROLLLOCK = SCROLL_LOCK = 0x47
    NUMLOCK = NUM_LOCK = 0x53
    PAUSE = 0x48
    INSERT = 0x49

    HOME = 0x4A
    PAGEUP = PAGE_UP = 0x4B
    DELETE = DELETE_FORWARD = 0x4C
    END = 0x4D
    PAGEDOWN = PAGE_DOWN = 0x4E

    ARROW_RIGHT = 0x4F
    ARROW_LEFT = 0x50
    ARROW_DOWN = 0x51
    ARROW_UP = 0x52

    APPLICATION = 0x65
    EXECUTE = 0x74
    HELP = 0x75
    MENU = 0x76
    SELECT = 0x77

    class Modifiers:
        CONTROL_LEFT = 0xE0
        SHIFT_LEFT = 0xE1
        ALT_LEFT = 0xE2
        GUI_LEFT = 0xE3
        CONTROL_RIGHT = 0xE4
        SHIFT_RIGHT = 0xE5
        ALT_RIGHT = 0xE6
        GUI_RIGHT = 0xE7

    def __class_getitem__(cls, item: str):
        if len(item) == 1:
            # A-Z
            if 'a' <= item.lower() <= 'z':
                return 0x04 + (ord(item.lower()) - ord('a'))
            # 1-9
            if '1' <= item <= '9':
                return 0x1E + (ord(item) - ord('1'))
            # 0
            if item == '0':
                return 0x27     # In ASCII, it's 0..9, but keyboard scancodes is 1..0
            # SPACE
            if item == ' ':
                return cls.SPACEBAR
            # Special symbols
            if item in cls.__SYMBOLS:
                return cls.__SYMBOLS[item]
        # Function keys
        if function_key := re.match(f'F(\d+)', item, re.IGNORECASE):
            number = int(function_key.group(1))
            if 1 <= number <= 12:
                return 0x3A + number - 1
            if 13 <= number <= 24:
                return 0x68 + number - 13
        # Modifier keys
        if hasattr(cls.Modifiers, item):
            return getattr(cls.Modifiers, item)
        # If not found, try class attributes
        return getattr(cls, item)


class KeyboardGadget(HIDGadget):
    def __init__(self, device, key_count=6, auto_update=False):
        HIDGadget.__init__(self, device, auto_update)
        self.keys = []
        self.key_count = key_count
        self.modifier_keys = []

    def to_bytes(self) -> bytes:
        modifiers = 0
        for key in self.modifier_keys:
            modifiers |= 1 << (key - KeyboardScanCode.Modifiers.CONTROL_LEFT)
        keys = bytes(self.keys).ljust(self.key_count, b'\x00')
        return modifiers.to_bytes(1, 'little') + b'\x00' + keys

    def press(self, key: Union[str, int]):
        if isinstance(key, str):
            key = KeyboardScanCode[key]
        if key is None:
            raise ValueError('Unknown key')
        if KeyboardScanCode.Modifiers.CONTROL_LEFT <= key <= KeyboardScanCode.Modifiers.GUI_RIGHT:
            self.modifier_keys.append(key)
        else:
            self.keys.append(key)
        if self.auto_update:
            self.update()

    def release(self, key: Union[str, int]):
        if isinstance(key, str):
            key = KeyboardScanCode[key]
        if key is None:
            raise ValueError('Unknown key')
        if KeyboardScanCode.Modifiers.CONTROL_LEFT <= key <= KeyboardScanCode.Modifiers.GUI_RIGHT:
            if key in self.modifier_keys:
                self.modifier_keys.remove(key)
        else:
            if key in self.keys:
                self.keys.remove(key)
        if self.auto_update:
            self.update()

    def press_and_release(self, key: Union[str, int]):
        self.press(key)
        self.update()
        self.release(key)
        self.update()


if __name__ == '__main__':
    js_data = JoystickGadget('/tmp/jsdata.bin', 2,2,10)
    js_data.set_button(5, True)
    print(js_data)
