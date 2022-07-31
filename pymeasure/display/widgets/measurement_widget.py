# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 11:57:38 2022

@author: mazzotti
"""

from ..Qt import QtGui
from .tab_widget import TabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import numpy as np
from tkinter import Tk, filedialog
from pymeasure.experiment import Procedure
from pymeasure.experiment import IntegerParameter, FloatParameter
from pymeasure.experiment import Results
from pymeasure.experiment import Worker

import logging

from ..log import LogHandler
from ..Qt import QtGui
from .tab_widget import TabWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())




class MeasurementWidget(TabWidget, QtGui.QWidget):
    """ Widget to display measurement information in Gui

    It is recommended to include this widget in all subclasses of
    :class:`ManagedWindowBase<pymeasure.display.windows.ManagedWindowBase>`
    """

    def __init__(self, name, procedure, parent=None):
        super().__init__(name, parent)
        self._setup_ui()
        self._layout()
        self.start = 0
        self.end = 0
        self.step = 0
        self.runs = 0
        self.file = None
        self.path = None

    def _setup_ui(self):
        self.view = QtGui.QPlainTextEdit()
        self.view.setReadOnly(True)
        

    def _layout(self):
        self.Measurement()
        
    def Measurement(self):
        layout = QVBoxLayout()
        controlsGroup = QHBoxLayout()
        controlsGroup.setSpacing(10)
        controlsGroup.addWidget(QLabel("Measurement"))
        start = QLabel("Start")
        self.boxStart = QSpinBox(self)
        self.boxStart.setRange(0, 40)
        self.boxStart.setMinimum(0)
        # adding action to the spin box
        self.boxStart.valueChanged.connect(self.register_start)
        controlsGroup.addWidget(start)
        controlsGroup.addWidget(self.boxStart)
        end = QLabel("End")
        self.boxEnd = QSpinBox(self)
        self.boxEnd.setRange(0, 40)
        self.boxEnd.setMinimum(0)
        self.boxEnd.valueChanged.connect(self.register_end)
        controlsGroup.addWidget(end)
        controlsGroup.addWidget(self.boxEnd)
        step = QLabel("Steps")
        self.boxStep = QSpinBox(self)
        self.boxStep.setRange(0, 40)
        self.boxStep.setMinimum(0)
        self.boxStep.valueChanged.connect(self.register_step)
        controlsGroup.addWidget(step)
        controlsGroup.addWidget(self.boxStep)
        
        runs = QLabel("Number of runs")
        self.boxRuns = QSpinBox(self)
        self.boxRuns.setMinimum(0)
        self.boxRuns.valueChanged.connect(self.register_runs)
        controlsGroup.addWidget(runs)
        controlsGroup.addWidget(self.boxRuns)
        
        #First Row of Widgets
        widgetControl = QWidget()
        widgetControl.setLayout(controlsGroup)
        layout.addWidget(widgetControl)
        
        
        #2nd row
        dataGroup = QHBoxLayout()
        dataGroup.setSpacing(10)
        dataGroup.addWidget(QLabel("Data"))
        widgetData = QWidget()
        widgetData.setLayout(dataGroup)
        layout.addWidget(widgetData)
        
        self.convert = QCheckBox("Convert data", self)
        dataGroup.addWidget(self.convert)
        self.convert.clicked.connect(self.convert_data)
        
        self.driveBack = QCheckBox("Drive Back", self)
        dataGroup.addWidget(self.driveBack)
        self.driveBack.clicked.connect(self.drive_back)
        
        self.saveData = QCheckBox("Save data", self)
        dataGroup.addWidget(self.saveData)
        self.saveData.setCheckable(True)
        self.saveData.clicked.connect(self.save_data)
        
        
        #3rd row: filename
        filenameGroup = QHBoxLayout()
        filenameGroup.setSpacing(10)
        filenameGroup.addWidget(QLabel("Filename"))
        widgetFilename = QWidget()
        widgetFilename.setLayout(filenameGroup)
        layout.addWidget(widgetFilename)
        self.filename = QLineEdit(self) 
        
        self.pb = QPushButton()
        self.pb.setObjectName("Enter")
        self.pb.setText("Enter")
        self.pb.clicked.connect(lambda: self.button_click(0))
        filenameGroup.addWidget(self.filename)
        filenameGroup.addWidget(self.pb)
        
        #4th row: filepath
        filepathGroup = QHBoxLayout()
        filepathGroup.setSpacing(10)
        filepathGroup.addWidget(QLabel("File path"))
        widgetPath = QWidget()
        widgetPath.setLayout(filepathGroup)
        layout.addWidget(widgetPath)
        self.filepath = QLineEdit(self) 
        self.pb1 = QPushButton()
        self.pb1.setObjectName("Browse Directory")
        self.pb1.setText("Browse Directory")
        self.pb1.clicked.connect(lambda: self.button_click(1))
        filepathGroup.addWidget(self.filepath)
        filepathGroup.addWidget(self.pb1)
        

        #Final Widget brining all together
        widget = QWidget()
        widget.setLayout(layout)
        self.setLayout(layout)
    
    def button_click(self, option):
        # shost is a QString object
        if(option == 0):
            self.file = self.filename.text()
            print (self.file)
        if(option == 1):
            self.path = self.filepath.text()
            root = Tk() # pointing root to Tk() to use it as Tk() in program.
            root.withdraw() # Hides small tkinter window.
            root.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.
            self.path = filedialog.askdirectory() # Returns opened path as str
            self.filepath.setText(self.path)
            print(self.path)
            
            
    
            
    
    def register_start(self):
        self.start = int(self.boxStart.value())
        print("start is: ", self.start)
    def register_end(self):
        self.end = int(self.boxEnd.value())
    def register_step(self):
        self.step = int(self.boxStep.value())
    def register_runs(self):
        self.runs = int(self.boxRuns.value())
        
    def calculate_iterations(self):
        self.iteration = self.runs*(self.end - self.start)/self.step
        self.iterations = np.linspace(0, self.iteration)
        
    def convert_data(self):
        self.convertData = True
    def drive_back(self):
        self.driveBack = True
    def save_data(self):
        self.saveData = True


        
        