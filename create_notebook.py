import nbformat as nbf

from utils import write_to_file


def create_notebook(docstring_blocks, code_blocks, output_file):
    nb = nbf.v4.new_notebook()
    for (file_docstring_blocks, file_code_blocks) in zip(docstring_blocks, code_blocks):
        for ((name, docstring), code) in zip(file_docstring_blocks, file_code_blocks):
            if docstring:
                formatted_docstring = "> " + docstring.replace("\n", "\n> ")
                markdown_docstring_cell = nbf.v4.new_markdown_cell(formatted_docstring)
                nb.cells.append(markdown_docstring_cell)
            code_cell = nbf.v4.new_code_cell(code)
            nb.cells.append(code_cell)
    write_to_file(output_file, nb, is_notebook=True)

