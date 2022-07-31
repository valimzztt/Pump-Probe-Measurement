# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 19:28:39 2022

@author: mazzotti
"""

import logging

from functools import partial

from ..inputs import BooleanInput, IntegerInput, ListInput, ScientificInput, StringInput
from ..Qt import QtCore, QtGui
from ...experiment import parameters

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class InputStagesWidget(QtGui.QWidget):
    """
    Widget wrapper for various :doc:`inputs`
    """

    # tuple of Input classes that do not need an external label
    NO_LABEL_INPUTS = (BooleanInput,)

    def __init__(self, procedure_class, inputs=(), parent=None, hide_groups=True):
        super().__init__(parent)
        self._procedure_class = procedure_class
        self._procedure = procedure_class()
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

    def _layout(self):
        vbox = QtGui.QHBoxLayout(self)
        vbox.setSpacing(15)

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
        self._procedure.set_parameters(parameter_values)
        return self._procedure