import pandas as pd
import os
import math
import numpy as np

path = r"C:\\Users\\Utente\\Desktop\\MPI_Stuttgart_Internship_Doc\\Python\\LabVIEW\\"
filename = "random_csv.csv"
file = r"C:\\Users\\Utente\\Desktop\\MPI_Stuttgart_Internship_Doc\\Python\\LabVIEW\\random_csv.csv"

columns = ["Stage position", "Voltage"]
class AveragerRuns():
    def __init__(self, procedure, columns):
        self.procedure = procedure
        self.path = procedure.get_parameter("path")
        self.filename =procedure.get_parameter("filename")
        self.datapoints = procedure.get_parameter("steps")
        self.runs = procedure.get_parameter("iterations")
        self.increment = procedure.get_parameter("increment")
        self.file = self.path + self.filename
        self.columns = columns


    def averaging(self):
        df = pd.read_csv(file,
                         sep=',',  # field separator
                         comment='#',  # comment
                         index_col=0,  # number or label of index column
                         skipinitialspace=True,
                         skip_blank_lines=True,
                         error_bad_lines=False,
                         warn_bad_lines=True
                         )

        folder = self.path + "singleRuns"
        if not os.path.exists(folder):
            os.makedirs(folder)

        datapoints = 100
        runs = 2
        steps = 100
        increment = 1
        nrows = df.index

        curr = datapoints
        compression_opts = dict(method='zip',
                                archive_name='out.csv')

        num_parameters = 3  # so we need to skip until 5
        chunks = pd.read_csv(file, skiprows=range(1, 5),
                             sep=',',  # field separator
                             comment='#',  # comment
                             index_col=None,  # number or label of index column
                             skipinitialspace=True,
                             skip_blank_lines=True,
                             error_bad_lines=False,
                             warn_bad_lines=True
                             )
        chunk_size = self.steps * self.increment
        stage = np.arange(100)

        if (chunks.shape[0] == self.runs * chunk_size):
            iterations = math.floor(df.shape[0] / datapoints)
            for i in range(self.iterations):
                chunk = pd.read_csv(self.file,
                                    skiprows=range(1, 6 + chunk_size * i), nrows=100,
                                    sep=',',  # field separator
                                    comment='#',  # comment
                                    index_col=None,  # number or label of index column
                                    skipinitialspace=True,
                                    skip_blank_lines=True,
                                    error_bad_lines=False,
                                    warn_bad_lines=True
                                    )

                chunk.to_csv(folder + r"\\" + "run" + str(i) + filename, header=("iteration", "voltage"), index=False)
        # means that a procedure has been interrupted

        else:
            i = 0
            curr = 0
            j = 0
            count = 1
            chunk = pd.read_csv(self.file,
                                skiprows=range(1, 6),
                                sep=',',  # field separator
                                comment='#',  # comment
                                index_col=None,  # number or label of index column
                                skipinitialspace=True,
                                skip_blank_lines=True,
                                error_bad_lines=False,
                                warn_bad_lines=True
                                )
            restart = False
            while curr < chunks.shape[0]:

                if (restart):
                    count = 1
                    print(" restarting")
                    j = 0
                    restart = False
                print("count", count)
                print("chunk", chunk.iat[curr, 0])
                print("stage", stage[j])
                if (chunk.iat[curr, 0] == stage[j]):
                    if (count % chunk_size == 0):
                        print("saving one run")
                        chunks = pd.read_csv(file,
                                             skiprows=range(1, 6 + i * chunk_size), sep=',',  # field separator
                                             comment='#',  # comment
                                             index_col=None,  # number or label of index column
                                             skipinitialspace=True,
                                             skip_blank_lines=True,
                                             error_bad_lines=False,
                                             warn_bad_lines=True
                                             )
                        chunks.to_csv(folder + r"\\" + "run" + str(i) + filename, header=("iteration", "voltage"),
                                      index=False)
                        i = i + 1
                        j = 0
                        count = 1
                        curr = curr + 1


                    else:
                        j = j + 1
                        curr = curr + 1
                        count = count + 1

                else:

                    restart = True






