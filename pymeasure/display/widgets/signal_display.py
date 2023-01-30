from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import *
from .tab_widget import TabWidget
from PyQt5.QtCore import QTimer


class SignalDisplayWidget(TabWidget, QWidget):
    def __init__(self, name, procedure, parent=None):
        super().__init__(name, parent)

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(False)
        self.procedure = procedure
        self.lockin = self.procedure.lockin
        self.signalLabel = QLabel("Signal")
        self.signalDisplay = QLineEdit(self)
        self.signalDisplay.setMaximumWidth(100)
        self.layout.addWidget(self.signalLabel)
        self.layout.addWidget(self.signalDisplay)
        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.showSignal)
        self.startTimer()

    def showSignal(self):
        signal = self.lockin.x
        self.signalDisplay.setText(str(signal))

    def startTimer(self):
        self.timer.start(1000)




