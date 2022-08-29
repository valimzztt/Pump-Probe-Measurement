# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
from PyQt5.QtWidgets import QMessageBox
from functools import partial

from ..inputs import BooleanInput, IntegerInput, ListInput, ScientificInput, StringInput
from ..Qt import QtCore, QtGui
from ...experiment import parameters
from tkinter import Tk, filedialog

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class InputsWidget(QtGui.QWidget):
    """
    Widget wrapper for various :doc:`inputs`
    """

    # tuple of Input classes that do not need an external label
    NO_LABEL_INPUTS = (BooleanInput,)

    def __init__(self, procedure_class, procedure, inputs=(), parent=None, hide_groups=True):
        super().__init__(parent)
        self._procedure_class = procedure_class
        self._procedure = procedure
        self._inputs = inputs
        self._setup_ui()
        self._layout()
        self._hide_groups = hide_groups
        self._setup_visibility_groups()

    def _setup_ui(self):
        parameter_objects = self._procedure.parameter_objects()
        
    
        for name in self._inputs:
            parameter = parameter_objects[name]
            if parameter.ui_class is not None:
                element = parameter.ui_class(parameter)

            elif isinstance(parameter, parameters.FloatParameter):
                element = ScientificInput(parameter)

            elif isinstance(parameter, parameters.IntegerParameter):
                element = IntegerInput(parameter)

            elif isinstance(parameter, parameters.BooleanParameter):
                element = BooleanInput(parameter)

            elif isinstance(parameter, parameters.ListParameter):
                element = ListInput(parameter)

            elif isinstance(parameter, parameters.Parameter):
                element = StringInput(parameter)

            setattr(self, name, element)

    def _layout1(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(6)

        self.labels = {}
        parameters = self._procedure.parameter_objects()
        for name in self._inputs:
            if not isinstance(getattr(self, name), self.NO_LABEL_INPUTS):
                label = QtGui.QLabel(self)
                label.setText("%s:" % parameters[name].name)
                vbox.addWidget(label)
                self.labels[name] = label

            vbox.addWidget(getattr(self, name))

        self.setLayout(vbox)
        
        
    def _layout(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(6)

        self.labels = {}
        parameters = self._procedure.parameter_objects()
        for name in self._inputs:

            if not isinstance(getattr(self, name), self.NO_LABEL_INPUTS):
  
                if name == "path":
                    filepathGroup = QtGui.QHBoxLayout()
                    filepathGroup.setSpacing(10)
                    labelPath = QtGui.QLabel(self)
                    labelPath.setText("%s:" % parameters[name].name)
                    filepathGroup.addWidget(labelPath)
                    filepathGroup.addWidget(getattr(self, name))
                    self.pathName = getattr(self, name)
                    self.labels[name] = labelPath
                    
                    widgetPath = QtGui.QWidget()
                    browse = QtGui.QPushButton()
                    browse.setObjectName("Browse Directory")
                    browse.setText("Browse Directory")
                    browse.clicked.connect(lambda: self._button_click(self.pathName, 1))
                    filepathGroup.addWidget(browse)
                    widgetPath.setLayout(filepathGroup)
                    vbox.addWidget(widgetPath)
                elif name == "filename":
                    #3rd row: filename
                    filenameGroup = QtGui.QHBoxLayout()
                    filenameGroup.setSpacing(10)
                    labelFileName = QtGui.QLabel(self)
                    labelFileName.setText("%s:" % parameters[name].name)
                    filenameGroup.addWidget(labelFileName)
                    self.fileNameBox = getattr(self, name)
                    filenameGroup.addWidget(getattr(self,name))
                    self.labels[name] = labelFileName
                    
                    enter = QtGui.QPushButton()
                    enter.setObjectName("Enter")
                    enter.setText("Enter")
                    enter.clicked.connect(lambda: self._button_click(self.fileNameBox, 0))
                    filenameGroup.addWidget(enter)
                    widgetFileName = QtGui.QWidget()
                    widgetFileName.setLayout(filenameGroup)
                    vbox.addWidget(widgetFileName)
                elif name == "waitingTime":
                    waiting = getattr(self, name)
                    self.waitingCheckBox = QtGui.QCheckBox(self)
                    waitingGroup = QtGui.QHBoxLayout()
                    waitingLabel = QtGui.QLabel(self)
                    self.waitingBox = QtGui.QSpinBox()
                    self.waitingBox.setValue(0)
                    if (self._procedure.get_parameter("waiting") == False):
                        self.waitingCheckBox.setChecked(False)
                        self.waitingBox.setEnabled(False)
                    else:
                        self.waitingCheckBox.setChecked(True)
                        self.waitingBox.setEnabled(True)
                    self.waitingCheckBox.clicked.connect(self.waitingOptionSetter)

                    waitingLabel.setText("%s:" % parameters[name].name)
                    waitingGroup.addWidget(waitingLabel)
                    self.waitingBox.valueChanged.connect(lambda: self.setWaitingTime(waiting))

                    self.driveBackLabel = QtGui.QLabel(self)
                    self.driveBackLabel.setText("Drive Back")
                    self.driveBackCheckBox = QtGui.QCheckBox(self)
                    if (self._procedure.get_parameter("driveBack") == False):
                        self.driveBackCheckBox.setChecked(False)
                    else:
                        self.driveBackCheckBox.setChecked(True)
                    self.driveBackCheckBox.clicked.connect(self.driveBackOptionSetter)


                    waitingGroup.addWidget(self.waitingBox)
                    waitingGroup.addWidget(self.waitingCheckBox)
                    waitingGroup.addWidget(self.driveBackLabel)
                    waitingGroup.addWidget(self.driveBackCheckBox)
                    self.labels[name] = waitingLabel
                    widgetWaiting = QtGui.QWidget()
                    widgetWaiting.setLayout(waitingGroup)
                    vbox.addWidget(widgetWaiting)

                    savingGroup = QtGui.QHBoxLayout()
                    self.saveLabel = QtGui.QLabel(self)
                    self.saveLabel.setText("Save data")
                    self.saveCheckBox = QtGui.QCheckBox(self)
                    if (self._procedure.get_parameter("saving") == False):
                        self.saveCheckBox.setChecked(False)
                    else:
                        self.saveCheckBox.setChecked(True)
                    self.saveCheckBox.clicked.connect(self.saveOptionSetter)

                    self.saveRunsLabel = QtGui.QLabel(self)
                    self.saveRunsLabel.setText("Save single runs")
                    self.saveRunsCheckBox = QtGui.QCheckBox(self)
                    if (self._procedure.get_parameter("saveRuns") == False):
                        self.saveRunsCheckBox.setChecked(False)
                    else:
                        self.saveRunsCheckBox.setChecked(True)
                    self.saveRunsCheckBox.clicked.connect(self.saveRunsOptionSetter)

                    savingGroup.addWidget(self.saveLabel)
                    savingGroup.addWidget(self.saveCheckBox)
                    savingGroup.addWidget(self.saveRunsLabel)
                    savingGroup.addWidget(self.saveRunsCheckBox)
                    self.labels["saveRuns"] = self.saveRunsLabel

                    widgetSaving = QtGui.QWidget()
                    widgetSaving.setLayout(savingGroup)


                    checkLayout =  QtGui.QVBoxLayout()
                    checkLayout.addWidget(widgetWaiting)
                    checkLayout.addWidget(widgetSaving)
                    widgetCheck= QtGui.QWidget()
                    widgetCheck.setLayout(checkLayout)
                    vbox.addWidget(widgetCheck)

                else:
                    label = QtGui.QLabel(self)
                    label.setText("%s:" % parameters[name].name)
                    vbox.addWidget(label)
                    self.labels[name] = label
                    vbox.addWidget(getattr(self, name))

        self.setLayout(vbox)

    def saveOptionSetter(self):
        if (self.saveCheckBox.checkState() == 2):
            self._procedure.set_parameter("saving", True)

        elif (self.saveCheckBox.checkState() == 0):
            self._procedure.set_parameter("saving", False)

    def saveRunsOptionSetter(self):
        if (self.saveRunsCheckBox.checkState() == 2):
            self._procedure.set_parameter("saveRuns", True)

        elif (self.saveRunsCheckBox.checkState() == 0):
            self._procedure.set_parameter("saveRuns", False)


    def driveBackOptionSetter(self):
        if (self.driveBackCheckBox.checkState() == 2):
            self._procedure.set_parameter("driveBack", True)
            self.driveBackCheckBox.setChecked(True)
        elif (self.driveBackCheckBox.checkState() == 0):
            #driveBack will always be true, can be changed easily
            self._procedure.set_parameter("driveBack", True)
            self.driveBackCheckBox.setChecked(True)

    def waitingOptionSetter(self):
        if(self.waitingCheckBox.checkState() == 2):
            self._procedure.set_parameter("waiting", True)
            self.waitingBox.setEnabled(True)
        elif(self.waitingCheckBox.checkState() == 0):
            self._procedure.set_parameter("waiting", False)
            self.waitingBox.setEnabled(False)

    def setWaitingTime(self, waiting):
        waiting.setValue(int(self.waitingBox.text()))
        self._procedure.set_parameter("waitingTime", int(self.waitingBox.text()))
        



    def _button_click(self, textBox, option):
        if option == 0:
            return
        if option == 1:
            root = Tk() # pointing root to Tk() to use it as Tk() in program.
            root.withdraw() # Hides small tkinter window.
            root.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.
            pathDirectory = filedialog.askdirectory() # Returns opened path as str
            textBox.setValue(pathDirectory)
            print(self.pathName.text())
            self._procedure.set_parameter("path", self.pathName.text())
            self._procedure.set_path(self.pathName.text())

        
    def _setup_visibility_groups(self):
        groups = {}
        parameters = self._procedure.parameter_objects()
        for name in self._inputs:
            parameter = parameters[name]

            group_state = {g: True for g in parameter.group_by}

            for group_name, condition in parameter.group_by.items():
                if group_name not in self._inputs or group_name == name:
                    continue

                if isinstance(getattr(self, group_name), BooleanInput):
                    # Adjust the boolean condition to a condition suitable for a checkbox
                    condition = QtCore.Qt.CheckState.Checked if condition else QtCore.Qt.CheckState.Unchecked  # noqa: E501

                if group_name not in groups:
                    groups[group_name] = []

                groups[group_name].append((name, condition, group_state))

        for group_name, group in groups.items():
            
            toggle = partial(self.toggle_group, group_name=group_name, group=group)
            group_el = getattr(self, group_name)
            if isinstance(group_el, BooleanInput):
                group_el.stateChanged.connect(toggle)
                toggle(group_el.checkState())
            elif isinstance(group_el, StringInput):
                group_el.textChanged.connect(toggle)
                toggle(group_el.text())
            elif isinstance(group_el, (IntegerInput, ScientificInput)):
                group_el.valueChanged.connect(toggle)
                toggle(group_el.value())
            elif isinstance(group_el, ListInput):
                group_el.currentTextChanged.connect(toggle)
                toggle(group_el.currentText())
            else:
                raise NotImplementedError(
                    f"Grouping based on {group_name} ({group_el}) is not implemented.")

    def toggle_group(self, state, group_name, group):
        for (name, condition, group_state) in group:
            if callable(condition):
                group_state[group_name] = condition(state)
            else:
                group_state[group_name] = (state == condition)

            visible = all(group_state.values())

            if self._hide_groups:
                getattr(self, name).setHidden(not visible)
            else:
                getattr(self, name).setDisabled(not visible)

            if name in self.labels:
                if self._hide_groups:
                    self.labels[name].setHidden(not visible)
                else:
                    self.labels[name].setDisabled(not visible)

    def set_parameters(self, parameter_objects):
        for name in self._inputs:
            element = getattr(self, name)
            element.set_parameter(parameter_objects[name])
            
    def get_procedure(self):
        """ Returns the current procedure """
        self._procedure = self._procedure_class()
        parameter_values = {}

        for name in self._inputs:
            element = getattr(self, name)
            parameter_values[name] = element.parameter.value

        parameter_values["waitingTime"] = int(self.waitingBox.text())
        parameter_values["path"] = self.pathName.text()
        if (self.driveBackCheckBox.checkState() == 2):
            parameter_values["driveBack"] = True
        elif (self.driveBackCheckBox.checkState() == 0):
            parameter_values["driveBack"] = False

        if (self.saveCheckBox.checkState() == 2):
            parameter_values["saving"] = True
        elif (self.saveCheckBox.checkState() == 0):
            parameter_values["saving"] = False

        if (self.saveRunsCheckBox.checkState() == 2):
            parameter_values["saveRuns"] = True
        elif (self.saveRunsCheckBox.checkState() == 0):
            parameter_values["saveRuns"] = False

        self._procedure.set_parameters(parameter_values)


        return self._procedure


