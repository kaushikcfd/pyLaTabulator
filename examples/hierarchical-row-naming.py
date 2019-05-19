from pyLaTabulator import Table
import numpy as np

data = np.array([
    [1.0, 3.0],
    [2.0, 4.0],
    [7.0, 9.0],
    [8.0, 8.5],
    [6.2, 8.4],
    [7.1, 5.2]])
column_names = ['SCPT', 'GCD']
row_names = [['Mass', 'Laplace', 'Helmholtz'], ['N=1', 'N=2', 'N=1', 'N=2',
    'N=1', 'N=2']]


class HRuleAddedTable(Table):
    def hrule_adder(self, i):
        if ((i+1) < data.shape[0]) and ((i+1) % 2 == 0):
            return r"\midrule[0.1pt]"
        else:
            return ""


HRuleAddedTable(data, column_names, row_names).display()
# HRuleAddedTable(data, column_names, row_names).generate()
