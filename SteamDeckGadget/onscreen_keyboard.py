from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QBrush, QPen, QFont
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout, QSpacerItem


class Keyboard(QWidget):
    keypress = pyqtSignal(str)

    def __init__(self, keys):
        QWidget.__init__(self)
        self.setLayout(QVBoxLayout())
        for i,row in enumerate(keys):
            widget = KeyboardRow(row)
            widget.keypress.connect(self.onscreen_keypress_event)
            self.layout().addWidget(widget)
            self.layout().setStretch(i, 1)
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

    def onscreen_keypress_event(self, key):
        self.keypress.emit(key)


class KeyboardRow(QWidget):
    keypress = pyqtSignal(str)

    def __init__(self, keys):
        QWidget.__init__(self)
        self.setLayout(QHBoxLayout())
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
            self.layout().addWidget(btn)
            self.layout().setStretch(i, int(key['width']*10))

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

    def onscreen_keypress_event(self, key):
        self.keypress.emit(key)


class KeyboardKey(QWidget):
    keypress = pyqtSignal(str)

    def __init__(self, name: str, label=None, lower=None, upper=None, **kwargs):
        QWidget.__init__(self)
        self.key = name
        self.label = label if label is not None else name
        self.label_lower = lower if lower is not None else self.label.lower()
        self.label_upper = upper if upper is not None else self.label.upper()
        self.font = QFont('Arial', 15)

    def mousePressEvent(self, a0) -> None:
        self.keypress.emit(self.key)

    def paintEvent(self, a0) -> None:
        painter = QPainter(self)
        painter.setBrush(QBrush(Qt.black))
        rect = QRect(3, 3, self.width()-6, self.height()-6)
        painter.drawRect(rect)
        painter.setPen(QPen(Qt.white))
        # print(painter.font().setPointSize(20))
        painter.setFont(self.font)
        painter.drawText(rect, Qt.AlignCenter, self.label)

    def resizeEvent(self, a0) -> None:
        self.font = QFont('Arial', self.height() // 2)

    def lowercase(self):
        self.label = self.label_lower

    def uppercase(self):
        self.label = self.label_upper

if __name__ == '__main__':
    import json
    app = QApplication([])
    with open('keyboard.json') as f:
        keys = json.load(f)
    key = Keyboard(keys)
    key.keypress.connect(print)
    key.show()
    app.exec()
