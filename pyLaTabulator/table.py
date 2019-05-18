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

        assert isinstance(data, np.ndarray)
        assert isinstance(column_names, list)
        assert isinstance(row_names, list)
        assert all(isinstance(col_name, str) for col_name in column_names)
        assert all(isinstance(row_name, str) for row_name in row_names)
        assert len(row_names) == data.shape[0]
        assert len(column_names) == data.shape[1]

        # }}}

        self.data = data
        self.row_names = row_names
        self.column_names = column_names

    def generate(self, filename=None):
        result_template = r"""\documentclass[11pt]{article}
\thispagestyle{empty}
\begin{document}
\begin{center}
\begin{tabular}{l${'r'*len(col_names)}}
\hline

  &  ${'  &  '.join(col_names)}\\\

\hline
% for (row_name, data_i) in zip(row_names, data):
${row_name}\
% for data_ij in data_i:
  &  ${data_ij}\
% endfor
\\\

% endfor

\hline
\end{tabular}
\end{center}
\end{document}
"""
        result = Template(result_template).render(
            row_names=self.row_names, col_names=self.column_names,
            data=self.data)
        ext = filename[-4:]

        if filename is None:
            print(result)
        elif ext == ".tex":
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
                subprocess.call(('pdfcrop -margin 3 {0}'.format(
                    gen_pdf_filename)).split())
                cropped_pdf = gen_pdf_filename[:-4]+'-crop.pdf'
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
