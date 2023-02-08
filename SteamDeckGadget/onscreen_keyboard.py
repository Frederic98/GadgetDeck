from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QBrush, QPen, QFont
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout, QSpacerItem


class Keyboard(QWidget):
    keypress = pyqtSignal(str)
    keyrelease = pyqtSignal(str)

    def __init__(self, keys):
        QWidget.__init__(self)
        self.setLayout(QVBoxLayout())
        self.rows = []
        for i,row in enumerate(keys):
            widget = KeyboardRow(row)
            widget.keypress.connect(self.onscreen_keypress_event)
            widget.keyrelease.connect(self.onscreen_keyrelease_event)
            self.rows.append(widget)
            self.layout().addWidget(widget)
            self.layout().setStretch(i, 1)
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

    def onscreen_keypress_event(self, key):
        self.keypress.emit(key)

    def onscreen_keyrelease_event(self, key):
        self.keyrelease.emit(key)

    def set_key_state(self, kwargs):
        for widget in self.rows:
            widget.set_key_state(**kwargs)


class KeyboardRow(QWidget):
    keypress = pyqtSignal(str)
    keyrelease = pyqtSignal(str)

    def __init__(self, keys):
        QWidget.__init__(self)
        self.setLayout(QHBoxLayout())
        self.keys = []
        for i,key in enumerate(keys):
            if isinstance(key, str):
                key = {'name': key}
            if 'width' not in key:
                key['width'] = 1.0
            if key.get('type', None) == 'spacer':
                btn = QWidget()
            else:
                btn = KeyboardKey(**key)
                btn.keypress.connect(self.onscreen_keypress_event)
                btn.keyrelease.connect(self.onscreen_keyrelease_event)
                self.keys.append(btn)
            self.layout().addWidget(btn)
            self.layout().setStretch(i, int(key['width']*10))

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

    def onscreen_keypress_event(self, key):
        self.keypress.emit(key)

    def onscreen_keyrelease_event(self, key):
        self.keyrelease.emit(key)

    def set_key_state(self, **kwargs):
        for widget in self.keys:
            widget.set_key_state(**kwargs)


class KeyboardKey(QWidget):
    keypress = pyqtSignal(str)
    keyrelease = pyqtSignal(str)

    _subclasses = {}
    def __new__(cls, name, *args, **kwargs):
        if cls is KeyboardKey:
            keytype = kwargs.get('type', name)
            if keytype in KeyboardKey._subclasses:
                cls = KeyboardKey._subclasses[keytype]
            return super().__new__(cls)

    def __init_subclass__(cls, key=None):
        if key is not None:
            KeyboardKey._subclasses[key] = cls

    def __init__(self, name: str, **kwargs):
        QWidget.__init__(self)
        self.key = name
        self.kwargs = kwargs
        self.font = QFont('Arial', 15)
        self.key_states = {'capslock': False, 'shift': False, 'numlock': False, 'scrolllock': False}
        self.pressed = False

    @property
    def label(self):
        if self.key_states['shift'] and self.kwargs.get('shift') is not None:
            return self.kwargs['shift']
        if self.kwargs.get('label') is not None:
            return self.kwargs['label']
        label = self.key
        # Capslock and Shift work like XOR - if one of them is active, capitalize the letter
        capitalized = self.key_states['shift'] != self.key_states['capslock']
        return label.upper() if capitalized else label.lower()

    def mousePressEvent(self, a0) -> None:
        self.keypress.emit(self.key)
        self.pressed = True
        self.update()

    def mouseReleaseEvent(self, a0) -> None:
        self.keyrelease.emit(self.key)
        self.pressed = False
        self.update()

    def paintEvent(self, a0) -> None:
        painter = QPainter(self)
        if self.pressed:
            painter.setBrush(QBrush(Qt.gray))
        else:
            painter.setBrush(QBrush(Qt.black))
        rect = QRect(3, 3, self.width()-6, self.height()-6)
        painter.drawRect(rect)
        painter.setPen(QPen(Qt.white))
        painter.setFont(self.font)
        painter.drawText(rect, Qt.AlignCenter, self.label)

    def resizeEvent(self, a0) -> None:
        self.font = QFont('Arial', self.height() // 2)

    def set_key_state(self, **kwargs):
        self.key_states.update(kwargs)
        self.update()


class CapslockKey(KeyboardKey, key='CAPSLOCK'):
    def mousePressEvent(self, a0) -> None:
        self.keypress.emit(self.key)

    def mouseReleaseEvent(self, a0) -> None:
        self.keyrelease.emit(self.key)

    def set_key_state(self, capslock=None, **kwargs):
        if capslock is not None:
            self.pressed = capslock
            self.update()


class LatchingKey(KeyboardKey, key='LATCHING'):
    def mousePressEvent(self, a0) -> None:
        if self.pressed:
            self.keyrelease.emit(self.key)
        else:
            self.keypress.emit(self.key)

    def mouseReleaseEvent(self, a0) -> None:
        pass


class ShiftKey(LatchingKey, key='SHIFT'):
    def set_key_state(self, shift=None, **kwargs):
        if shift is not None:
            self.pressed = shift
            self.update()


class ControlKey(LatchingKey, key='CONTROL'):
    def set_key_state(self, control=None, **kwargs):
        if control is not None:
            self.pressed = control
            self.update()


class AltKey(LatchingKey, key='ALT'):
    def set_key_state(self, alt=None, **kwargs):
        if alt is not None:
            self.pressed = alt
            self.update()


class GuiKey(LatchingKey, key='GUI'):
    def set_key_state(self, gui=None, **kwargs):
        if gui is not None:
            self.pressed = gui
            self.update()


class FunctionKey(KeyboardKey, key='FUNCTION'):
    @property
    def label(self):
        return self.key.upper()

if __name__ == '__main__':
    import json
    app = QApplication([])
    with open('keyboard.json') as f:
        keys = json.load(f)
    key = Keyboard(keys)
    key.keypress.connect(print)
    key.show()
    app.exec()
