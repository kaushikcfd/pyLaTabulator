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

        if all(isinstance(row_name, str) for row_name in row_names):
            row_names = [row_names]

        assert isinstance(data, np.ndarray)
        assert isinstance(column_names, list)
        assert isinstance(row_names, list)
        assert all(isinstance(col_name, list) for col_name in column_names)
        assert all(isinstance(row_name, list) for row_name in row_names)
        assert all((data.shape[1] % len(col_name)) == 0
                for col_name in column_names)
        assert all((data.shape[0] % len(row_name)) == 0
                for row_name in row_names)

        # }}}

        self.data = data
        self.row_names = row_names
        self.column_names = column_names

    def format(self, i, j):
        return str(self.data[i, j])

    def hrule_adder(self, i):
        return ""

    def preamble(self):
        return ""

    def generate(self, filename=None):
        formatted_data = np.ndarray(shape=self.data.shape, dtype=np.dtype('U25'))
        rule = np.ndarray(shape=self.data.shape[0], dtype=np.dtype('U25'))
        for i in range(self.data.shape[0]):
            for j in range(self.data.shape[1]):
                formatted_data[i, j] = self.format(i, j)

            rule[i] = self.hrule_adder(i)

        result_template = r"""\documentclass[11pt]{article}
\usepackage{multirow}
\usepackage{booktabs}
${preamble}

\thispagestyle{empty}
\begin{document}
\begin{table}
\begin{tabular}{${'c'*(data.shape[1]+len(row_names))}}
\toprule
% for col_name in col_names:
<%
    cols_per_cell = data.shape[1] // len(col_name)
    alignment = 'c'
    delimiter = r'} & \multicolumn{' + str(cols_per_cell) + r'}{' + alignment +r'}{'  # noqa
%>
\multicolumn{${len(row_names)}}{c}{} ${delimiter[2:]}${delimiter.join(col_name)}}\\\
% endfor


\midrule

% for i in range(data.shape[0]):
    % for row_name in row_names:
        <% nrows_per_row_name = data.shape[0] // len(row_name) %>
${r'\multirow{%d}{*}{%s}' % (nrows_per_row_name,
row_name[i//nrows_per_row_name]) if i % nrows_per_row_name == 0 else '  '}  & \
    % endfor
    ${'  &  '.join(elem for elem in data[i, :])}\\\

${rule[i]}
% endfor

\bottomrule
\end{tabular}
\end{table}
\end{document}
"""
        result = Template(result_template).render(row_names=self.row_names,
                col_names=self.column_names, data=formatted_data,
                preamble=self.preamble(), rule=rule)

        if filename is None:
            print(result)
            return

        ext = filename[-4:]
        if ext == ".tex":
            # if the desired output is tex only, then only extract the tabular
            # part.
            resultlines = result.split("\n")
            begintabular_idx, = [i for i, line in enumerate(resultlines)
                                 if line.startswith(r"\begin{tabular}")]
            endtabular_idx, = [i for i, line in enumerate(resultlines)
                               if line.startswith(r"\end{tabular}")]

            result = "\n".join(resultlines[begintabular_idx:endtabular_idx+1])

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
