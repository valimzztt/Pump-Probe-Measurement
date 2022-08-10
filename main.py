# This is a sample Python script.

"""
Created on Tue Jun  7 14:13:05 2022

@author: mazzotti
"""


import numpy as np
from pymeasure.experiment import Procedure
from pymeasure.experiment import Results
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter, ListParameter, BooleanParameter
from time import sleep
import tempfile
import logging
import PyQt5.QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from pymeasure.instruments.newport.esp300 import ESP300
import sys
from csv import DictWriter
import pandas as pd
from PyQt5 import QtGui

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())



# Step 1: Create a worker class
class WorkerPositionError(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, procedure, controller):
        super().__init__()
        self.procedure = procedure
        self.controller = controller

    def run(self):
        self.progress.emit(0)

        sleep(10)
        self.finished.emit()


class RandomProcedure(Procedure):
    # initialize all the class attributes
    controller = ESP300("GPIB0::1::INSTR")

    # parameters of the procedure
    iterations = IntegerParameter('Loop Iterations', default=3)
    #delay = FloatParameter('Delay Time', units='s', default=0.2)
    start = IntegerParameter("start", units="mm", default=0)
    steps = IntegerParameter("steps", default=20)
    increment = FloatParameter("increment", default=1)

    filename = Parameter("filename", default="default")
    saving = BooleanParameter("saving", default=True)
    path = Parameter("path", default=r"C:\Users\us_measurement\PycharmProjects")
    axis = ListParameter("axis", [1, 2, 3])
    waitingTime = IntegerParameter('Waiting time', default=0)
    driveBack = BooleanParameter("Drive Back", default=True)
    waiting = BooleanParameter("Waiting", default= False)


    end = start.value + increment.value * steps.value

    DATA_COLUMNS = ["Voltage", "Stage_Position", "Range", "Average"]
    abortedProcedure = IntegerParameter('Aborted procedure', default=0)

#in order to make sure that only procedure that are completely executed are being saved

    def execute(self):
        # we need to monitor that the position of tha stage matches exactly the range we have set and we do it without any worker so on the MainThread
        # default will be stage 1
        # first set the correct stage/axis
        # start a separate thread here
        # create a QThread which is a handler and start the worker hat is handled by it
        self.data_filename = self.path + "\\" + self.filename + ".csv"
        self.stage = self.selectStage()
        self.end = self.start + self.increment * self.steps
        self.checkStageParameters()
        self.setStageAtStartPosition()


        self.startPositionStage = self.stage.position

        self.range_x = np.linspace(self.start, self.end, self.steps + 1)
        self.data_points = self.steps + 1
        self.averages = 50
        self.max_current = self.end
        self.min_current = self.start
        self.scale = np.linspace(0, 50, self.data_points)
        i = 0


        if (self.current_iter == 0):
            with open(self.data_filename, 'w', newline='') as csvfile:
                dictwriter_object = DictWriter(csvfile, fieldnames=self.DATA_COLUMNS)
                dictwriter_object.writeheader()
                for point in self.range_x:
                    self.lockin.reset_buffer()
                    sleep(0.1)
                    self.lockin.start_buffer()
                    self.move_stage(point)

                    log.info("we can continue to retrieve data")
                    data_measurement = {
                        'Voltage': self.lockin.x, "Stage_Position": self.stage.position, "Range": point, "Average": 0
                    }
                    data_measurement["Average"] = data_measurement.get("Voltage")
                    self.emit('results', data_measurement)

                    sleep(0.01)
                    dictwriter_object.writerow(data_measurement)

                    if self.should_stop():
                        log.info("User aborted the procedure")
                        # TODO: REMEMBER TO SAVE THE DATA TO FILE
                        break
                    i = i +1

        else:
            df = pd.read_csv(self.data_filename)
            row = 0
            sum_voltages = []
            for point in self.range_x:
                self.lockin.reset_buffer()
                sleep(0.1)
                self.lockin.start_buffer()
                self.move_stage(point)
                print(self.stage.position)
                data_measurement = {
                    'Voltage': self.lockin.x, "Stage_Position": self.stage.position, "Range": point,"Average": 0
                }

                sum_voltage = (self.current_iter * df.at[row, "Average"] + data_measurement.get("Voltage")) / (
                        self.current_iter + 1)
                data_measurement["Average"] = sum_voltage
                self.emit('results', data_measurement)
                sleep(0.01)

                sum_voltages.append(sum_voltage)

                row = row + 1

                if self.should_stop():
                    log.info("User aborted the procedure")
                    break
            if(len(sum_voltages) == len(self.range_x)):
                i = 0
                for sum_voltage in sum_voltages:
                    df.at[i, "Average"] = sum_voltage
                    df.to_csv(self.data_filename, index=False)
                    i = i +1

        if(self.driveBack):
            print("Driving back")
            print(self.start)
            print(self.stage.position)
            self.move_stage(int(self.startPositionStage))

    def move_stage(self, position):
        self.stage.write("PA" + str(position))
        while not self.stage.motion_done:
            sleep(0.05)
        log.info("stage has been moved")

    def setStageAtStartPosition(self):
        if(self.current_iter != 0):
            if(self.driveBack):
                self.stage.write("PA" + str(self.start))
                while not self.stage.motion_done:
                    sleep(0.05)
                log.info("StAGE HAS BEEN SET AT START POSITION")
        else:
            self.stage.write("PA" + str(self.start))
            while not self.stage.motion_done:
                sleep(0.05)
            log.info("Beginning")


    def selectStage(self):
        if (self.axis == 1):
            self.stage = self.controller.x
        elif (self.axis == 2):
            self.stage = self.controller.y
        elif (self.axis == 3):
            self.stage = self.controller.phi
        return self.stage

    def checkStageParameters(self):
        #TODO: add checking of parameters

        if(self.start > self.stage.right_limit):
            self.showErrorStartPosition(self)


    def showStageError(self, stage):
        """Error Box that displays error in startin"""
        mb = MyMessageBox()
        mb.setText("The selected axis is not enabled")
        info = ["Axis used: " + str(self.axis)]
        mb.setDetailedText( "\n".join(info))
        mb.exec()

    def showErrorStartPosition(self):

        """Error Box that displays error in startin"""
        mb = QMessageBox()
        mb.setText("Wrong start position value")
        info = ["Axis used: " + str(self.axis), "Left limit: " + str(self.stage.left_limit),
                "Right limit: " + str(self.stage.stage_limit)]
        mb.setDetailedText( "\n".join(info))
        mb.exec()
        pass

    def showErrorEndPosition(self):
        mb = MyMessageBox()
        mb.setText("Wrong end position values")
        info = ["Axis used: " + str(self.procedure.get_parameter("axis")), "Left limit: " + str(self.stage.right_limit),
                "Right limit: " + str(self.stage.left_limit)]
        mb.setDetailedText("\n".join(info))
        mb.exec()

    def shutdown(self):
        log.info("Finished measuring Random Procedure")

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end
    def set_waitingTime(self, waitingTime):
        self.waitingTime = waitingTime


class MyMessageBox(QMessageBox):
    def __init__(self):
        QtGui.QMessageBox.__init__(self)
        self.setSizeGripEnabled(True)

    def event(self, e):
        result = QtGui.QMessageBox.event(self, e)

        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        textEdit = self.findChild(QtGui.QTextEdit)
        if textEdit != None :
            textEdit.setMinimumHeight(0)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(0)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        return result

class MainWindow(ManagedWindow):

    def __init__(self):
        # Connect and configure the instrument
        log.info("Connecting and configuring the instrument")

        super().__init__(
            procedure_class=RandomProcedure,
            inputs=['iterations', "start", "steps", "increment", "filename", "path", "axis", "driveBack", "waitingTime", "waiting"],
            inputComand=["start", "steps", "increment", "filename", "path"],
            inputStages=["1", "2"],
            displays=['iterations', "start", "steps", "increment", "filename", "path", "axis", "driveBack", "waitingTime","waiting"],
            x_axis="Range",
            y_axis='Voltage'
        )

        self.setWindowTitle('Lock-in Amplifier')
        self.manager.abort_returned.connect(self.changeIteration)
        self.manager.finished.connect(self.finishedIteration)
        self.manager.finished.connect(self.checkFinishedProcedure)
        self.iterations = None
        self.should_run = True
        self.curr = 0
        self.stage = None

    def finishedIteration(self):
        self.curr = self.curr + 1

    def checkFinishedProcedure(self):
        if(self.curr == self.procedure.get_parameter("iterations")):
            self.curr = 0


    def changeIteration(self):
        if (self.should_run):
            filename = tempfile.mktemp()
            procedure = self.make_procedure()
            procedure.set_current_iteration(procedure.get_parameter("iterations") - 1)
            if (procedure.saving):
                path = procedure.get_parameter("path")
                filename_loc = procedure.get_parameter("filename")
                self.data_filename = path + "/" + filename_loc + ".csv"
                #we are going to delete it
                temporaryfile = path + "/" + "added.csv"
                results = Results(procedure, (filename, temporaryfile))
            else:
                results = Results(procedure, filename)
            experiment = self.new_experiment(results, procedure.get_parameter("iterations") - 1)
            self.manager.queue(experiment)



    def queue(self):
        self.procedure = self.make_procedure()
        self.iterations = self.procedure.get_parameter("iterations")
        self.driveBack = self.procedure.get_parameter("driveBack")

        curr = 0
        self.setStage()
        self.checkPositionParameter()

        while (curr < self.iterations):
            if (self.should_run):
                filename = tempfile.mktemp()
                procedure = self.make_procedure()
                procedure.set_current_iteration(curr)
                if (procedure.saving):
                    path = procedure.get_parameter("path")
                    filename_loc = procedure.get_parameter("filename")
                    self.data_filename = path + "/" + filename_loc + ".csv"
                    temporaryfile = path + "/" + "averaging.csv"
                    results = Results(procedure, (filename, temporaryfile))
                else:
                    results = Results(procedure, filename)
                experiment = self.new_experiment(results, curr)
                self.manager.queue(experiment)
                curr = curr + 1

    def setStage(self):
        self.axis = self.procedure.axis
        if (self.axis == 1):
            self.stage = self.controller.x
        elif (self.axis == 2):
            self.stage = self.controller.y
        elif (self.axis == 3):
            self.stage = self.controller.phi



    # we need to check that:
    # 1)position parameters are within the limit of the state
    # 2)the stage we are using is enabled/there is a stage
    # 3)we need to move the stage we are using to the given starting position
    def checkPositionParameter(self):
        if self.stage is None:
            self.thread = QThread()
            self.worker = WorkerPositionError(self.procedure, self.controller)
            self.worker.moveToThread(self.thread)
            # Step 5: Connect signals and slots
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            #self.worker.progress.connect(lambda: self.showStageError(self.stage))
            self.thread.start()


        elif (self.procedure.start < self.stage.left_limit or self.procedure.start > self.procedure.end or self.procedure.start > self.stage.right_limit):
            self.thread = QThread()
            self.worker = WorkerPositionError(self.procedure, self.controller)
            self.worker.moveToThread(self.thread)
            # Step 5: Connect signals and slots
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            #self.worker.progress.connect(lambda: self.showErrorStartPosition(self.stage))

            self.thread.start()

        elif (self.procedure.end < self.stage.left_limit or self.procedure.end > self.stage.right_limit):
            self.thread = QThread()
            self.worker = WorkerPositionError(self.procedure, self.controller)
            self.worker.moveToThread(self.thread)
            # Step 5: Connect signals and slots
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()
            #self.worker.progress.connect(lambda: self.showErrorEndPosition(self.stage))


    def moveStage(self):
        self.axis = self.procedure.axis
        self.stage.define_position(self.procedure.get_parameter("start"))

    def get_start(self):
        return self.start


if __name__ == "__main__":
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("QLabel{font-size: 11pt;}")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


