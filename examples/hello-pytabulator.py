from pyLaTabulator import Table
import numpy as np

data = np.array([
    [1.0, 2.0],
    [3.0, 4.0]])
row_names = ['R1', 'R2']
column_names = ['C1', 'C2']

Table(data, column_names, row_names).generate('danda.tex')
