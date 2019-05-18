import numpy as np
from mako.template import Template
import string
import random
import subprocess
from PIL import Image
import matplotlib.pyplot as plt


class Table(object):
    def __init__(self, data, column_names, row_names):

        # {{{ sanity checks

        if all(isinstance(col_name, str) for col_name in column_names):
            column_names = [column_names]

        assert isinstance(data, np.ndarray)
        assert isinstance(column_names, list)
        assert isinstance(row_names, list)
        assert all(isinstance(col_name, list) for col_name in column_names)
        assert all(isinstance(row_name, str) for row_name in row_names)
        assert len(row_names) == data.shape[0]
        assert all((data.shape[1] % len(col_name)) == 0
                for col_name in column_names)

        # }}}

        self.data = data
        self.row_names = row_names
        self.column_names = column_names

    def format(self, i, j):
        return str(self.data[i, j])

    def preamble(self):
        return ""

    def generate(self, filename=None):
        formatted_data = np.ndarray(shape=self.data.shape, dtype=np.dtype('U25'))
        for i in range(self.data.shape[0]):
            for j in range(self.data.shape[1]):
                formatted_data[i, j] = self.format(i, j)

        result_template = r"""\documentclass[11pt]{article}
\usepackage{booktabs}
${preamble}

\thispagestyle{empty}
\begin{document}
\begin{table}
\begin{tabular}{c${'c'*data.shape[1]}}
\toprule
% for col_name in col_names:
<%
    cols_per_cell = data.shape[1] // len(col_name)
    alignment = 'c'
    delimiter = r'} & \multicolumn{' + str(cols_per_cell) + r'}{' + alignment +r'}{'  # noqa
%>
\multicolumn{1}{c}{} ${delimiter[2:]}${delimiter.join(col_name)}}\\\
% endfor


\midrule

% for i in range(data.shape[0]):
${row_names[i]}\
% for j in range(data.shape[1]):
  &  ${data[i, j]}\
% endfor
\\\

% endfor

\bottomrule
\end{tabular}
\end{table}
\end{document}
"""
        result = Template(result_template).render(row_names=self.row_names,
                col_names=self.column_names, data=formatted_data,
                preamble=self.preamble())

        if filename is None:
            print(result)
            return

        ext = filename[-4:]
        if ext == ".tex":
            with open(filename, 'w') as f:
                f.write(result)
        elif ext == ".pdf" or ext == ".png":
            tex_filename = ('/tmp/' +
                    ''.join(random.choice(string.ascii_letters) for _ in
                        range(9)) + '.tex')
            gen_pdf_filename = tex_filename[:-4] + '.pdf'
            with open(tex_filename, 'w') as f:
                f.write(result)
            subprocess.call(('pdflatex -output-directory=/tmp {0}'.format(
                tex_filename)).split())
            if ext == ".pdf":
                subprocess.call(('mv {0} {1}'.format(
                    gen_pdf_filename, filename)).split())
            if ext == ".png":
                cropped_pdf = gen_pdf_filename[:-4]+'-crop.pdf'
                subprocess.call(('pdfcrop -margin 3 {0} {1}'.format(
                    gen_pdf_filename, cropped_pdf)).split())
                with open(filename, 'w') as f:
                    ppm = subprocess.Popen(('pdftoppm -r 500 {0}'.format(
                        cropped_pdf)).split(), stdout=subprocess.PIPE)
                    subprocess.call(['pnmtopng'], stdin=ppm.stdout, stdout=f)
                    ppm.wait()
        else:
            raise NotImplementedError()

    def display(self):
        png_filename = ('/tmp/' +
                ''.join(random.choice(string.ascii_letters) for _ in
                    range(9)) + '.png')
        self.generate(png_filename)
        plt.imshow(Image.open(png_filename))
        plt.show()
