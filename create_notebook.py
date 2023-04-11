import nbformat as nbf


def create_notebook(docstring_blocks, code_blocks, output_file):
    nb = nbf.v4.new_notebook()
    for (file_docstring_blocks, file_code_blocks) in zip(docstring_blocks, code_blocks):
        for ((name, docstring), code) in zip(file_docstring_blocks, file_code_blocks):
            if name and name not in {'is_class_included', 'is_method_included'}:
                markdown_name_cell = nbf.v4.new_markdown_cell(f'## {name}')
                nb.cells.append(markdown_name_cell)
            if docstring:
                markdown_docstring_cell = nbf.v4.new_markdown_cell(docstring)
                nb.cells.append(markdown_docstring_cell)
            code_cell = nbf.v4.new_code_cell(code)
            nb.cells.append(code_cell)
    with open(output_file, 'w') as f:
        nbf.write(nb, f)