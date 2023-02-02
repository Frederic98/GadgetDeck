#!/usr/bin/python3
import math
import struct
from typing import BinaryIO


class JoystickData:
    def __init__(self, js_count, trig_count, btn_count, callback=None):
        btn_bytes = math.ceil(btn_count / 8)

        self.joysticks = [[0,0] for _ in range(js_count)]
        self.triggers = [0 for _ in range(trig_count)]
        self.buttons = [0 for _ in range(btn_bytes)]
        self.struct = struct.Struct('<' + 'b'*(js_count*2) + 'b'*trig_count + 'B'*btn_bytes)
        self.callback = callback if callback is not None else (lambda: None)

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

    def set_joystick(self, i: int, x: float, y: float):
        self.joysticks[i][0] = int(self.remap(x, -1, 1, -127, 127))
        self.joysticks[i][1] = int(self.remap(y, -1, 1, -127, 127))
        self.callback()

    def set_trigger(self, i: int, v: float):
        self.triggers[i] = int(self.remap(v, -1, 1, -127, 127))
        self.callback()

    def set_button(self, i: int, v: bool):
        if v:
            self.buttons[i//8] |= (1 << (i%8))
        else:
            self.buttons[i//8] &= ~(1 << (i%8))
        self.callback()

    def __repr__(self):
        js = " ".join([f"({x} {y})" for x,y in self.joysticks])
        trig = " ".join(str(v) for v in self.triggers)
        btn = " ".join(f"{v:>08b}" for v in self.buttons)
        return f'<{self.__class__.__qualname__} {js} - {trig} - {btn}>'

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


class JoystickGadget:
    def __init__(self, device: str):
        self.device: BinaryIO = open(device, 'wb+')
        self.data = JoystickData(2, 1, 16)

    def close(self):
        """End Joystick_8"""
        self.data.reset()
        self.update()
        self.device.close()

    def update(self):
        self.device.write(self.data.to_bytes())
        self.device.flush()


if __name__ == '__main__':
    js_data = JoystickData(2,2,10)
    js_data.set_button(5, True)
    print(js_data)
