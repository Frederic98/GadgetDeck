from PyQt5.QtCore import pyqtSignal, QPoint, Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, qApp


def constrain(value, lo, hi):
    return max(lo, min(value, hi))


class JoystickUI(QWidget):
    _update_info_signal = pyqtSignal(object)

    def __init__(self):
        QWidget.__init__(self)
        self.main_layout = QVBoxLayout()
        self.controller_label = QLabel('Controller ID')
        self.main_layout.addWidget(self.controller_label)
        self.actionset_label = QLabel('Action Set ID')
        self.main_layout.addWidget(self.actionset_label)
        self.analog_action_label = QLabel('Analog Action')
        self.main_layout.addWidget(self.analog_action_label)
        self.digital_action_label = QLabel('Digital Action')
        self.main_layout.addWidget(self.digital_action_label)
        self.js = AnalogWidget()
        self.main_layout.addWidget(self.js)
        self.exit_button = QPushButton('Exit')
        self.exit_button.clicked.connect(self.exit)
        self.main_layout.addWidget(self.exit_button)
        self.setLayout(self.main_layout)
        self.setWindowState(Qt.WindowMaximized)

        self.data = {}
        self._update_info_signal.connect(self._update_information_listener)

    def update_information(self, data):
        self.data.update(data)
        self._update_info_signal.emit(self.data)

    def _update_information_listener(self, data):
        if 'controller' in data:
            self.controller_label.setText(f"Controllers: {data['controller']}")
        if 'action_set' in data:
            self.actionset_label.setText(f"Action sets: {data['action_set']}")
        if 'analog_action' in data:
            self.analog_action_label.setText(f"Analog actions: {data['analog_action']}")
        if 'digital_action' in data:
            self.digital_action_label.setText(f"Digital actions: {data['digital_action']}")
        if 'analog_data' in data:
            self.js.set_value(data['analog_data'])

    def exit(self):
        self.close()
        qApp.quit()

    @property
    def qApp(self):
        return qApp


class AnalogWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.main_layout = QHBoxLayout()

        self.trigger_left = TriggerWidget()
        self.main_layout.addWidget(self.trigger_left)
        self.joystick_left = JoystickWidget()
        self.main_layout.addWidget(self.joystick_left)
        self.joystick_right = JoystickWidget()
        self.main_layout.addWidget(self.joystick_right)
        self.trigger_right = TriggerWidget()
        self.main_layout.addWidget(self.trigger_right)

        self.setLayout(self.main_layout)

    def set_value(self, data):
        self.joystick_left.set_value(data['JoyLeft'].x, data['JoyLeft'].y)
        self.joystick_right.set_value(data['JoyRight'].x, data['JoyRight'].y)
        self.trigger_left.set_value(data['TrigLeft'].x)
        self.trigger_right.set_value(data['TrigRight'].x)


class JoystickWidget(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setMinimumSize(100, 100)
        self.js_position = [0,0]

    def set_value(self, x, y):
        self.js_position[0] = constrain(x, -1, 1)
        self.js_position[1] = constrain(y, -1, 1) * -1
        self.update()

    def paintEvent(self, a0) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        center = QPoint(int(self.width() / 2), int(self.height() / 2))
        radius = int((min(self.width(), self.height()) - 1) / 2)

        painter.setPen(QPen(Qt.black))
        painter.setBrush(QBrush(Qt.lightGray))
        # painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(center, radius, radius)

        painter.setPen(QPen(Qt.black))
        painter.setBrush(QBrush(Qt.black))
        dot_radius = radius / 1.5
        dot_x = int(self.js_position[0] * (radius - dot_radius)) + center.x()
        dot_y = int(self.js_position[1] * (radius - dot_radius)) + center.y()
        painter.drawEllipse(QPoint(dot_x, dot_y), dot_radius, dot_radius)
        # painter.drawEllipse(0,0,99,99)


class TriggerWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.value = 0.0
        self.setMinimumSize(25, 50)

    def set_value(self, value):
        self.value = value
        self.update()

    def paintEvent(self, a0) -> None:
        painter = QPainter(self)
        padding = 5

        painter.setPen(QPen(Qt.black))
        painter.setBrush(QBrush(Qt.white))
        painter.drawRect(self.rect())

        painter.setBrush(QBrush(Qt.black))
        bottom_right = QPoint(self.width() - padding, self.height() - padding)
        top_left = bottom_right - QPoint(int(self.width() - 2*padding), int((self.height() - 2*padding) * self.value))
        painter.drawRect(QRect(top_left, bottom_right))


if __name__ == '__main__':
    app = QApplication([])
    ui = JoystickUI()
    ui.show()
    app.exec()
