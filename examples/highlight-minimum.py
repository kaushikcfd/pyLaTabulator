from pyLaTabulator import Table
import numpy as np

data = np.array([
    [1.0, 4.0, 9.0, 8.0],
    [3.0, 2.0, 7.0, 8.5]])
row_names = ['SCPT', 'GCD']
column_names = [['Mass', 'Laplace'], ['N=1', 'N=2', 'N=1', 'N=2']]


class HighlightMinTable(Table):
    def preamble(self):
        return r"\usepackage{xcolor}"

    def format(self, i, j):
        if i == np.argmin(self.data[:, j]):
            return r"{\color{green} " + "{0}".format(self.data[i, j]) + "}"
        else:
            return "{0}".format(self.data[i, j])


HighlightMinTable(data, column_names, row_names).display()
# HighlightMinTable(data, column_names, row_names).generate('highlight-min.png')
