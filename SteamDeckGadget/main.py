
# Force steam input lock onto our program
# steam steam://forceinputappid/480

import threading

from PyQt5.QtWidgets import QApplication
import joystick_ui
from steamworks import STEAMWORKS
import usb_gadget


class JoystickEmulator:
    ACTION_SETS = ('InGameControls',)
    ANALOG_ACTIONS = ('JoyLeft', 'JoyRight', 'TrigLeft', 'TrigRight', 'Mouse')
    DIGITAL_ACTIONS = ('A', 'B', 'X', 'Y', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'BumpLeft', 'BumpRight', 'Menu', 'Start', 'JoyPressLeft', 'JoyPressRight',
                       'BackLeftTop', 'BackLeftBottom', 'BackRightTop', 'BackRightBottom')
    DIGITAL_MOUSE_ACTIONS = ('MouseClickLeft', 'MouseClickRight')

    def __init__(self):
        gadget = usb_gadget.USBGadget('steam_gadget')
        self.js_gadget = self.mouse_gadget = self.keyboard_gadget = None
        if gadget['functions'].exists('hid.joystick'):
            print('Joystick gadget found')
            hid_joystick = usb_gadget.HIDFunction(gadget, 'joystick')
            self.js_gadget = usb_gadget.JoystickGadget(hid_joystick.device, 2, 2, 24)
        if gadget['functions'].exists('hid.mouse'):
            print('Mouse gadget found')
            hid_mouse = usb_gadget.HIDFunction(gadget, 'mouse')
            self.mouse_gadget = usb_gadget.MouseGadget(hid_mouse.device, 2, 8, 2)
        if gadget['functions'].exists('hid.keyboard'):
            print('Keyboard gadget found')
            hid_keyboard = usb_gadget.HIDFunction(gadget, 'keyboard')
            self.keyboard_gadget = usb_gadget.KeyboardGadget(hid_keyboard.device, 6)

        self.window = joystick_ui.JoystickUI()
        self.window.keypress.connect(self.onscreen_keypress_event)
        self.steam = STEAMWORKS()
        self.steam.initialize()
        self.steam.Input.Init()
        self.controllers = self.steam.Input.GetConnectedControllers()
        self.action_set = self.steam.Input.GetActionSetHandle(self.ACTION_SETS[0])
        self.analog_actions = {name: self.steam.Input.GetAnalogActionHandle(name) for name in self.ANALOG_ACTIONS}
        self.digital_actions = {name: self.steam.Input.GetDigitalActionHandle(name) for name in self.DIGITAL_ACTIONS}
        self.digital_actions.update({name: self.steam.Input.GetDigitalActionHandle(name) for name in self.DIGITAL_MOUSE_ACTIONS})

        data = {'controller': self.controllers,
                'action_set': self.action_set,
                'analog_action': self.analog_actions,
                'digital_action': self.digital_actions}
        self.window.update_information(data)
        self.js_thread = threading.Thread(target=self.steam_worker, daemon=True)
        self.js_thread.start()

    def steam_worker(self):
        while True:
            self.steam.Input.RunFrame()
            if self.controllers:
                controller = self.controllers[0]
                analog_data = {action: self.steam.Input.GetAnalogActionData(controller, handle) for action, handle in self.analog_actions.items()}
                digital_data = {action: self.steam.Input.GetDigitalActionData(controller, handle).bState for action, handle in self.digital_actions.items()}
                data = {'analog_data': analog_data, 'digital_action': digital_data}
                self.window.update_information(data)

                if self.js_gadget is not None:
                    self.js_gadget.set_joystick(0, analog_data['JoyLeft'].x, -1 * analog_data['JoyLeft'].y)
                    self.js_gadget.set_joystick(1, analog_data['JoyRight'].x, -1 * analog_data['JoyRight'].y)
                    self.js_gadget.set_trigger(0, analog_data['TrigLeft'].x)
                    self.js_gadget.set_trigger(1, analog_data['TrigRight'].x)
                    for i, btn in enumerate(self.DIGITAL_ACTIONS):
                        self.js_gadget.set_button(i, digital_data[btn])
                    self.js_gadget.update()
                if self.mouse_gadget is not None:
                    self.mouse_gadget.move(analog_data['Mouse'].x, analog_data['Mouse'].y)
                    self.mouse_gadget.set_button(0, digital_data['MouseClickLeft'])
                    self.mouse_gadget.set_button(1, digital_data['MouseClickRight'])
                    self.mouse_gadget.update()
            else:
                self.controllers = self.steam.Input.GetConnectedControllers()
                for controller in self.controllers:
                    self.steam.Input.ActivateActionSet(controller, self.action_set)
                self.window.update_information({'controller': self.controllers})

    def onscreen_keypress_event(self, key):
        if self.keyboard_gadget is not None:
            self.keyboard_gadget.press_and_release(key)

if __name__ == '__main__':
    app = QApplication([])
    emulator = JoystickEmulator()
    emulator.window.show()
    app.exec()


# gadget = JoystickGadget('/dev/hidg0')
#
# steam = STEAMWORKS()
# steam.initialize()
# steam.Input.Init()
# steam.Input.RunFrame()
# controllers = steam.Input.GetConnectedControllers()
# action_sets = {name: steam.Input.GetActionSetHandle(name) for name in ('InGameControls',)}
# analog_actions = {name: steam.Input.GetAnalogActionHandle(name) for name in ('JoyLeft', 'JoyRight', 'TrigLeft', 'TrigRight')}
# button_names = ('A', 'B', 'X', 'Y', 'BumpLeft', 'BumpRight', 'Menu', 'Start', 'JoyPressLeft', 'JoyPressRight')
# button_names = ('A', 'B', 'X', 'Y', 'BumpLeft', 'BumpRight', 'Menu', 'Start')
# digital_actions = {name: steam.Input.GetDigitalActionHandle(name) for name in button_names}
# if controllers:
#     steam.Input.ActivateActionSet(controllers[0], action_sets['InGameControls'])
# data = {'controller': controllers,
#         'action_set': action_sets,
#         'analog_action': analog_actions,
#         'digital_action': digital_actions}
# widget.update_information(data)

# def thread_worker():
#     time.sleep(1)
#     while True:
#         steam._cdll.RunCallbacks()
#         steam.Input.RunFrame()
#         # controllers = ', '.join(f'{c:X}' for c in steam.Input.GetConnectedControllers())
#         # action_sets = ', '.join([f'{handle}: {steam.Input.GetActionSetHandle(handle)}' for handle in ('InGameControls','MenuControls')])
#         # data = {'controller': 'Connected controllers: ' + controllers,
#         #         'action_set': 'Action sets: ' + action_sets}
#         # data = {'analog_action': str(steam.Input.GetAnalogActionHandle('Move'))}
#         if controllers:
#             analog_data = {action: steam.Input.GetAnalogActionData(controllers[0], analog_actions[action]) for action in analog_actions}
#             digital_data = {action: steam.Input.GetDigitalActionData(controllers[0], digital_actions[action]).bState for action in digital_actions}
#             data = {'analog_data': analog_data, 'digital_action': digital_data}
#             widget.update_information(data)
#             gadget.data.set_joystick(0, analog_data['JoyLeft'].x, -1*analog_data['JoyLeft'].y)
#             gadget.data.set_joystick(1, analog_data['JoyRight'].x, -1*analog_data['JoyRight'].y)
#             gadget.data.set_trigger(0, analog_data['TrigLeft'].x - analog_data['TrigRight'].x)
#             for i,btn in enumerate(button_names):
#                 gadget.data.set_button(i, digital_data[btn])
#             gadget.update()
#         time.sleep(0.1)

# threading.Thread(target=thread_worker, daemon=True).start()
# app.exec()
