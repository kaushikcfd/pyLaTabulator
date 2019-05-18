from pyLaTabulator import Table
import numpy as np

data = np.array([
    [1.0, 2.0, 7.0, 8.0],
    [3.0, 4.0, 9.0, 8.5]])
row_names = ['SCPT', 'GCD']
column_names = [['Mass', 'Laplace'], ['N=1', 'N=2', 'N=1', 'N=2']]

Table(data, column_names, row_names).display()
# Table(data, column_names, row_names).generate()
