# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 15:23:19 2022

@author: mazzotti
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 15:04:14 2022

@author: mazzotti
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 22:32:49 2022

@author: mazzotti
"""



import logging
from ..log import LogHandler
from ..Qt import QtGui
from .tab_widget import TabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import re
from decimal import Decimal

import pymeasure
from pymeasure.instruments.srs import SR830
import pymeasure.display.inputs

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ParametersWidget(TabWidget, QtGui.QWidget):
    """ Widget to display logging information in GUI

    It is recommended to include this widget in all subclasses of
    :class:`ManagedWindowBase<pymeasure.display.windows.ManagedWindowBase>`
    """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._setup_ui()
        self._layout()
        #initializes the lockin amplifier to control
        self.lockin = SR830("GPIB::8")
        
        


    def _setup_ui(self):
        self.view = QtGui.QPlainTextEdit()
        self.view.setReadOnly(True)
        

    def _layout(self):
        up = QVBoxLayout()
        up.addWidget(self.TimeConstant())
        up.addWidget(self.Sensitivity())
        up.addWidget(self.FilterSlopes())



        
        down = QHBoxLayout()
        down.addWidget(self.Input())
        down.addWidget(self.InputConfig())
        down.addWidget(self.inputNotchConfig())

        
        w1 = QWidget()
        w1.setLayout(up)
        w2 = QWidget()
        w2.setLayout(down)
        
        
        self.layout =  QVBoxLayout()
        self.layout.addWidget(w1)
        self.layout.addWidget(w2)
        
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setLayout(self.layout)
    def Input(self):
        layout = QVBoxLayout()
        header = QVBoxLayout()
        header.addStretch(0)
        grounding = QVBoxLayout()
        grounding.setSpacing(10)
        grounding.addStretch(0)
        
        b1 = QRadioButton ("Float")
        b1.setChecked(True)
        b2 = QRadioButton ("Grounds")
        grounding.addWidget(QLabel("Input Groundings"))
        grounding.addWidget(b1)
        grounding.addWidget(b2)
        b1.clicked.connect(lambda: self.setInputGroundings(0))
        b2.clicked.connect(lambda: self.setInputGroundings(1))
        
        coupling = QVBoxLayout()
        coupling.setSpacing(10)
        coupling.addStretch(0)
        
        b3 = QRadioButton ("AC")
        b3.setChecked(True)
        b4 = QRadioButton ("DC")
        coupling.addWidget(QLabel("Input Couplings"))
        coupling.addWidget(b3)
        coupling.addWidget(b4)
        b3.clicked.connect(lambda: self.setInputCouplings(0))
        b4.clicked.connect(lambda: self.setInputCouplings(1))
        
        w1 = QWidget()
        w1.setLayout(grounding)
        w2 = QWidget()
        w2.setLayout(coupling)
        layout.addWidget(w1)
        layout.addWidget(w2)

        w_final = QWidget()
        w_final.setLayout(layout)
        return w_final
        
    def InputConfig(self):
        layout = QVBoxLayout()
        header = QVBoxLayout()
        header.addStretch(0)
        controlsGroup = QVBoxLayout()
        controlsGroup.setSpacing(10)
        controlsGroup.addStretch(0)
        
        b1 = QRadioButton ("A")
        b1.setChecked(True)
        b2 = QRadioButton ("A - B")
        b3 = QRadioButton ("I (1 MOhm)")
        b4 = QRadioButton ("I (100 MOhm)")
        controlsGroup.addWidget(b1)
        controlsGroup.addWidget(b2)
        controlsGroup.addWidget(b3)
        controlsGroup.addWidget(b4)
        
        b1.clicked.connect(lambda: self.setInputConfig(0))
        b2.clicked.connect(lambda: self.setInputConfig(1))
        b3.clicked.connect(lambda: self.setInputConfig(2))
        b4.clicked.connect(lambda: self.setInputConfig(3))
        
        w = QWidget()
        w.setLayout(controlsGroup)
        header.addWidget(QLabel("Input Configuration"))
        header.addWidget(w)
        
        w_final = QWidget()
        w_final.setLayout(header)
        layout.addWidget(w_final)
      
        #Final Widget brining all together
        widget = QWidget()
        widget.setLayout(layout)
        return widget

   # INPUT_CONFIGS = ['A', 'A - B', 'I (1 MOhm)', 'I (100 MOhm)']
    def setInputConfig(self, option):
        self.lockin.input_config = self.lockin.INPUT_CONFIGS[option]
    def setInputGroundings(self, option):
        self.lockin.input_grounding = self.lockin.INPUT_GROUNDINGS[option]
    def setInputCouplings(self, option):
        self.lockin.input_coupling = self.lockin.INPUT_COUPLINGS[option]

    def FilterSlopes(self):
        layout = QVBoxLayout()
        final_layout = QVBoxLayout()
        header = QVBoxLayout()
        header.addStretch(0)

        b1 = QRadioButton ("6 dB")
        b2 = QRadioButton ("12 dB")
        b3 = QRadioButton ("18 dB")
        b4 = QRadioButton ("24 dB")
        b1.setChecked(True)
        
        b1.clicked.connect(lambda: self.setFilterSlope(0))
        b2.clicked.connect(lambda: self.setFilterSlope(1))
        b3.clicked.connect(lambda: self.setFilterSlope(2))
        b4.clicked.connect(lambda: self.setFilterSlope(3))
        
        
        layout.addWidget(b1)
        layout.addWidget(b2)
        layout.addWidget(b3)
        layout.addWidget(b4)
        
        w = QWidget()
        w.setLayout(layout)
        header.addWidget(QLabel("Filter Slopes"))
        header.addWidget(w)
        
        w_final = QWidget()
        w_final.setLayout(header)
        return w_final
    
    def setFilterSlope(self, option):
        self.lockin.filter_slope = self.lockin.FILTER_SLOPES[option]

        
        

    
    def Sensitivity(self):
        layout = QHBoxLayout()
        self.cb = QComboBox()
        
        SENSITIVITIES = [
        2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9,
        500e-9, 1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6,
        200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3,
        50e-3, 100e-3, 200e-3, 500e-3, 1
        ]
        sens = [str(i) for i in SENSITIVITIES]
        self.cb.addItems(sens)
        self.cb.setCurrentIndex(6)
        self.cb.currentIndexChanged.connect(self.setSensitivity)

        self.sensitivity = QLabel("Sensitivity")
        #self.sensitivity.setStyleSheet("border: 2px solid black;")
        layout.addWidget(self.sensitivity)
        layout.addWidget(self.cb)
         
        widget  = QWidget()
        widget.setLayout(layout)
        return widget
    
    def setSensitivity(self):
        #set the sensitivty of the lockin amplifier to the given value
        self.lockin.sensitivity = float(self.cb.currentText())
        

    def inputNotchConfig(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.addStretch(0)
        
        b1 = QRadioButton ("None")
        b2 = QRadioButton ("Line")
        b3 = QRadioButton ("2 x Line")
        b4 = QRadioButton ("Both")
        
        layout.addWidget(QLabel("Input Notch Configurations"))
        layout.addWidget(b1)
        layout.addWidget(b2)
        layout.addWidget(b3)
        layout.addWidget(b4)
        b1.clicked.connect(lambda: self.setInputNotchConfig(1))
        b2.clicked.connect(lambda: self.setInputNotchConfig(2))
        b3.clicked.connect(lambda: self.setInputNotchConfig(3))
        b4.clicked.connect(lambda: self.setInputNotchConfig(4))
        
        #Final Widget brining all together
        widget = QWidget()
        widget.setLayout(layout)
        return widget
    
    def setInputNotchConfig(self, option):
        if(option == 1):
            self.lockin.input_notch_config = self.lockin.INPUT_NOTCH_CONFIGS[0]
        if(option == 2):
            self.lockin.input_notch_config = self.lockin.INPUT_NOTCH_CONFIGS[1]
        if(option == 3):
            self.lockin.input_notch_config = self.lockin.INPUT_NOTCH_CONFIGS[2]
        if(option == 4):
            self.lockin.input_notch_config = self.lockin.INPUT_NOTCH_CONFIGS[3]

    def TimeConstant(self):
        layout = QHBoxLayout()
        self.tc = QComboBox()

        time_constants= ["10 µs", "30 µs", "100 µs", "300 µs", "1 ms", "3 ms", "10 ms", "30 ms", "100 ms", "300 ms",
                          "1 s", "3 s", "10 s", "30 s", "300 s", "1000 s", "3000 s", "10 000 s", "30 000 s"]

        self.tc.addItems(time_constants)
        self.tc.setCurrentIndex(13)
        self.tc.currentIndexChanged.connect(self.setTime)

        layout.addWidget(QLabel("Time Constant"))
        layout.addWidget(self.tc)

        widget = QWidget()
        widget.setLayout(layout)
        return widget


    def setTime(self):
        time_constant = self.characters(self.tc.currentText())
        print(time_constant)
        TIME_CONSTANTS = [
            10e-6, 30e-6, 100e-6, 300e-6, 1e-3, 3e-3, 10e-3,
            30e-3, 100e-3, 300e-3, 1, 3, 10, 30, 100, 300, 1e3,
            3e3, 10e3, 30e3
        ]
        if(str(time_constant) == "1e-05"):
            self.lockin.time_constant = TIME_CONSTANTS[0]
        elif (time_constant == 3e-05):
            self.lockin.time_constant = TIME_CONSTANTS[1]

        else:

            self.lockin.time_constant = time_constant


    def characters(self, string):
        mag = int(re.sub(r'[^0-9]', '', str(string)))
        decimal = re.sub(r'[^a-zA-Z|µ]', '', str(string))
        print(decimal)
        num = 0
        scientific = 0
        if (decimal == "s"):
            scientific = int(mag)
        if (decimal == "µs"):
            scientific = float(str(mag) + "e-6")
        if (decimal == "ms"):
            num = float(mag * 0.001)
            scientific = float("{:.2e}".format(Decimal(num)))

        return scientific







            
    

    

