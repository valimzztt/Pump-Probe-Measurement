import pandas as pd
import os
import math
import numpy as np



#12 parameters, we need to skip 12 + 4 lines in the output file
columns = ["Stage position", "Voltage"]
class AveragerRuns():
    def __init__(self, procedure, columns):
        self.procedure = procedure
        self.path = procedure.get_parameter("path")
        self.filename = "averaging"
        self.datapoints = procedure.get_parameter("steps")
        self.iterations = procedure.get_parameter("iterations")
        self.increment = procedure.get_parameter("increment")
        self.file = self.path +"\\" + self.filename + ".csv"
        self.columns = columns
        self.folder = self.path + "\singleRuns"


    def averaging(self):
        df = pd.read_csv(self.file,
                         sep=',',  # field separator
                         comment='#',  # comment
                         index_col=0,  # number or label of index column
                         skipinitialspace=True,
                         skip_blank_lines=True,
                         on_bad_lines='skip'
                         )
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)


        chunks = pd.read_csv(self.file,
                             sep=',',  # field separator
                             comment='#',  # comment
                             index_col=None,  # number or label of index column
                             skipinitialspace=True,
                             skip_blank_lines=True,
                             on_bad_lines='skip'
                             )
        chunks = pd.read_csv(self.file, comment='#')
        chunk_size = self.datapoints + 1
        stage = np.arange(self.datapoints + 1)
        if (chunks.shape[0] == self.iterations * chunk_size):
            for i in range(self.iterations):
                print(self.datapoints)
                print(chunk_size * i)
                chunk = pd.read_csv(self.file,
                                    skiprows=range(2, 2+ chunk_size * i), nrows=self.datapoints + 1,
                                    sep=',',  # field separator
                                    comment='#',  # comment
                                    index_col=None,  # number or label of index column
                                    skipinitialspace=True,
                                    skip_blank_lines=True,
                                    error_bad_lines=False,
                                    warn_bad_lines=True
                                    )
                print(chunk)
                chunk = chunk[["Stage_Position", "Voltage"]]

                chunk.to_csv(self.folder + r"\\" + "run" + str(i) + self.filename, header=("Stage position", "voltage"),
                             index=False)
