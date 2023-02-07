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
                print(f'Initializing special keyboard key {cls}')
            return super().__new__(cls)

    def __init_subclass__(cls, key=None):
        print(f'registering keyboard key {key}')
        KeyboardKey._subclasses[key] = cls

    def __init__(self, name: str, label=None, shift=None, **kwargs):
        QWidget.__init__(self)
        self.key = name
        self.label = label if label is not None else name
        self.label_shift = shift
        self.font = QFont('Arial', 15)
        self.key_states = {'capslock': False, 'shift': False, 'numlock': False, 'scrolllock': False}
        self.pressed = False

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
        # print(painter.font().setPointSize(20))
        painter.setFont(self.font)
        if self.label_shift is not None and self.key_states['shift']:
            label = self.label_shift
        else:
            # Capslock and Shift work like XOR - if one of them is active, capitalize the letter
            capitalized = self.key_states['shift'] != self.key_states['capslock']
            label = self.label.upper() if capitalized else self.label.lower()
        painter.drawText(rect, Qt.AlignCenter, label)

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


class ShiftKey(KeyboardKey, key='SHIFT'):
    def mousePressEvent(self, a0) -> None:
        if self.pressed:
            self.keyrelease.emit(self.key)
        else:
            self.keypress.emit(self.key)
        # self.pressed = not self.pressed
        # self.update()

    def mouseReleaseEvent(self, a0) -> None:
        pass

    def set_key_state(self, shift=None, **kwargs):
        if shift is not None:
            self.pressed = shift
            self.update()


if __name__ == '__main__':
    import json
    app = QApplication([])
    with open('keyboard.json') as f:
        keys = json.load(f)
    key = Keyboard(keys)
    key.keypress.connect(print)
    key.show()
    app.exec()
