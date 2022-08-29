# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 19:34:07 2022

@author: mazzotti
"""


from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal

import logging


from ..Qt import QtGui
from .tab_widget import TabWidget


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
import time






class Worker1(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, axis, position):
        super().__init__()
        self.axis = axis
        self.moveToPosition(position)


    def moveToPosition(self, position):
        #this is the right command to move the stage
        self.axis.write("PA" + str(position))
        while not self.axis.motion_done:
            time.sleep(0.05)

    def run(self):
        self.progress.emit(int(self.axis.position))
        self.finished.emit()



class Worker2(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, axis, position):
        super().__init__()
        self.axis = axis
        self.moveToPosition(position)

    def moveToPosition(self, position):
        self.axis.write("PA" + str(position))
        while not self.axis.motion_done:
            time.sleep(0.05)



    def run(self):
        self.progress.emit(int(self.axis.position))
        self.finished.emit()


class Worker3(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, axis, position):
        super().__init__()
        self.axis = axis
        self.moveToPosition(position)

    def moveToPosition(self, position):
        self.axis.write("PA" + str(position))
        while not self.axis.motion_done:
            time.sleep(0.05)

    def run(self):
        self.progress.emit(int(self.axis.position))
        self.finished.emit()

        
#This Widget Class is used to move the stage to the exact position
  
class StageControllerWidget(TabWidget, QtGui.QWidget):
    """ Widget to display measurement information in Gui

    It is recommended to include this widget in all subclasses of
    :class:`ManagedWindowBase<pymeasure.display.windows.ManagedWindowBase>`
    """
    def __init__(self, name, procedure, parent=None):
        super().__init__(name, parent)
        self.layout = QVBoxLayout(self)
        
        self.procedure = procedure
        self.controller = self.procedure.controller
        self.start = procedure.start
        self.end = procedure.end

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Axis 1")
        self.tabs.addTab(self.tab2,"Axis 2")
        self.tabs.addTab(self.tab3,"Axis 3")
    
        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.currPosition1 = QLineEdit(self)
        self.currPosition2 = QLineEdit(self)
        self.currPosition3 = QLineEdit(self)
        
        
        self.position1 = QDoubleSpinBox(self)
        self.position1.setRange(-50, 50)
        
        self.tab1.layout.addWidget(QLabel("Set Position of Stage "))
        self.tab1.layout.addWidget(self.position1)

        self.move1 = QPushButton("Move")
        self.move1.setStyleSheet("background-color : grey")
        self.move1.clicked.connect(lambda: self.move(1))
        self.tab1.layout.addWidget(self.move1)
        hbox1 = QHBoxLayout(self)
        hbox1.setSpacing(10)
        hbox1.addWidget(QLabel("Current Position of Stage"))
        self.enabled1 = QPushButton("Enable motor", self)
        self.enabled1.clicked.connect(lambda:(self.enableMotor(self.controller.x, self.enabled1, self.currPosition1)))
        if (self.controller.x.enabled):
            self.enabled1.setText("Disable motor")
            self.currPosition1.setText(str(self.controller.x.position))
        else:
            self.enabled1.setText("Enable motor")
            self.currPosition1.setText("NO STAGE")

        hbox1.addWidget(self.currPosition1)
        hbox1.addWidget(self.enabled1)
        
        hboxWidget = QWidget()
        hboxWidget.setLayout(hbox1)
        self.tab1.layout.addWidget(hboxWidget)
        self.tab1.layout.setSpacing(0)
        self.tab1.setLayout(self.tab1.layout)
        
        # Create second tab
        self.tab2.layout = QVBoxLayout(self)
        self.position2 = QDoubleSpinBox(self)
        self.position2.setRange(-50, 50)
        
        self.tab2.layout.addWidget(QLabel("Set Position of Stage"))
        self.tab2.layout.addWidget(self.position2)
        self.move2 = QPushButton("Move")
        # changing color of button
        self.move2.setStyleSheet("background-color : grey")
        self.move2.clicked.connect(lambda: self.move(2))
        self.tab2.layout.addWidget(self.move2)
        
        hbox2 = QHBoxLayout(self)
        hbox2.setSpacing(10)
        hbox2.addWidget(QLabel("Current Position of Stage"))
        hbox2.addWidget(self.currPosition2)
        self.enabled2 = QPushButton("Enable motor", self)
        self.enabled2.clicked.connect(lambda: self.enableMotor(self.controller.y, self.enabled2, self.currPosition2))
        hbox2.addWidget(self.enabled2)

        if(self.controller.y.enabled):
            self.enabled2.setText("Disable motor")
            self.currPosition2.setText(str(self.controller.y.position))
        else:
            self.enabled2.setText("Enable motor")
            self.currPosition2.setText("NO STAGE")


        hboxWidget2 = QWidget()
        hboxWidget2.setLayout(hbox2)
        self.tab2.layout.addWidget(hboxWidget2)
        self.tab2.layout.setSpacing(0)
        self.tab2.setLayout(self.tab2.layout)
        
        
        
        # Create first tab
        self.tab3.layout = QVBoxLayout(self)
        self.position3 = QDoubleSpinBox(self)
        self.position3.setRange(-50, 50)
        self.tab3.layout.setSpacing(0)
        self.tab3.layout.addWidget(QLabel("Set Position of Stage"))
        self.tab3.layout.addWidget(self.position3)
        self.move3 = QPushButton("Move")
        self.move3.setStyleSheet("background-color : grey")
        self.move3.clicked.connect(lambda: self.move(3))
        self.tab3.layout.addWidget(self.move3)
        
        hbox3 = QHBoxLayout(self)
        hbox3.setSpacing(10)
        hbox3.addWidget(QLabel("Current Position of Stage"))
        hbox3.addWidget(self.currPosition3)

        self.enabled3 = QPushButton(self)
        hbox3.addWidget(self.enabled3)
        self.enabled3.clicked.connect(lambda: self.enableMotor(self.controller.phi, self.enabled3, self.currPosition3))
        if (self.controller.phi.enabled):
            self.enabled3.setText("Disable motor")
            self.currPosition3.setText(str(self.controller.phi.position))
        else:
            self.enabled3.setText("Enable motor")
            self.currPosition3.setText("NO STAGE")

        hboxWidget3 = QWidget()
        hboxWidget3.setLayout(hbox3)
        self.tab3.layout.addWidget(hboxWidget3)
        self.tab3.layout.setSpacing(0)
        self.tab3.setLayout(self.tab3.layout)
        

        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def enableMotor(self, axis, button, position):
        self.axis = axis
        self.enabled = button
        self.position = position
        if axis != None:
            if (self.enabled.text() == "Enable motor"):
                self.axis.enable()
                self.position.setText(str(axis.position))
                self.enabled.setText("Disable motor")
            else:
                self.axis.disable()
                self.enabled.setText("Enable motor")
                self.position.setText("Motor disabled")
        else:
            return



    def reportProgress(self, axis):
        if axis == 1:
            self.axis = self.controller.x
            self.position = self.controller.x.position
            self.currPosition1.setText(str(self.controller.x.position))
        if axis == 2:
            self.axis = self.controller.y
            self.position = self.axis.position
            self.currPosition2.setText(str(self.axis.position))
        else:
            self.axis = self.controller.phi
            position = self.axis.position
            self.currPosition3.setText(str(self.axis.position))
        msg = QMessageBox(1, "Information", "Stage has been moved to position " + str(self.position), QMessageBox.Ok)
        msg.exec()

    def move(self, axis):
        if (axis == 1):
            if(self.controller.x.enabled):

                self.moveStage(axis)
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setText("No stage enabled on Axis 1")
                msg.setIcon(QMessageBox.Warning)
                msg.exec()
        if(axis == 2):
            if (self.controller.y.enabled):
                self.moveStage(axis)
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setText("No stage enabled on Axis 2")
                msg.setIcon(QMessageBox.Warning)
                msg.exec()
        if (axis == 3):
            if(self.controller.phi.enabled):
                self.moveStage(axis)
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setText("No stage enabled on Axis 3")
                msg.setIcon(QMessageBox.Warning)
                msg.exec()


    def moveStage(self, axis):
        self.thread = QThread()
        if(axis == 1):
            self.worker = Worker1(self.controller.x,self.position1.value())
            self.move1.setEnabled(False)
            self.worker.finished.connect(
                lambda: self.move1.setEnabled(True)
            )

        if(axis == 2):

            self.worker = Worker2(self.controller.y,self.position2.value())
            self.move2.setEnabled(False)
            self.thread.finished.connect(
                lambda: self.move2.setEnabled(True)
            )
        if(axis == 3):
            self.worker = Worker3(self.controller.phi,self.position3.value())
            self.move3.setEnabled(False)
            self.thread.finished.connect(
                lambda: self.move3.setEnabled(True)
            )
        
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.worker.progress.connect(lambda: self.reportProgress(axis))
        self.thread.start()
            


    def _setup_ui(self):
        self.view = QtGui.QPlainTextEdit()
        self.view.setReadOnly(True)
