import ast
import os

from code_extractor import CodeExtractor
from utils import write_to_file


def extract_code(filenames, output_file, include_classes=None, include_methods=None, exclude_classes=None,
                 exclude_methods=None):
    desired_code_blocks = []
    docstrings = []
    extractor = CodeExtractor(include_classes, include_methods, exclude_classes, exclude_methods)
    file_code_blocks = []
    file_docstring_blocks = []
    for filename in filenames:
        with open(filename, 'r') as f:
            code = f.read()
        ast_tree = ast.parse(code)
        ast.fix_missing_locations(ast_tree)
        extractor.visit(ast_tree)
        desired_code = '\n'.join(extractor.code_blocks)
        docstrings.extend(extractor.docstrings)
        if desired_code:
            file_name_only = os.path.basename(filename)
            desired_code_blocks.append(f'# {file_name_only}:\n{desired_code}\n')
        file_code_blocks.append(extractor.code_blocks[:])  # Make a copy of the current code_blocks
        file_docstring_blocks.append(extractor.docstring_blocks[:])  # Make a copy of the current docstring_blocks
        extractor.code_blocks.clear()  # Clear the current code_blocks
        extractor.docstring_blocks.clear()  # Clear the current docstring_blocks
    write_to_file(output_file, desired_code_blocks, join_with_newline=True)
    extractor.code_blocks = file_code_blocks
    extractor.docstring_blocks = file_docstring_blocks
    return extractor
