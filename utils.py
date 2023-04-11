import ast
import fnmatch
import os

import pyperclip

from code_extractor import CodeExtractor


# utils.py:
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
    with open(output_file, 'w') as f:
        f.write('\n'.join(desired_code_blocks))
    extractor.code_blocks = file_code_blocks
    extractor.docstring_blocks = file_docstring_blocks
    return extractor


def filter_files(path, include=None, exclude=None, ignore_dirs=None, ignore_files=None):
    if ignore_dirs is None:
        ignore_dirs = ['__pycache__', '.pytest_cache', 'v', 'cache', '.git', '.idea', 'objects', 'info', 'logs', 'refs',
                       'hooks', 'inspectionProfiles', 'b2', 'pack', '00', '6c', 'e6', 'heads', 'tags', 'remotes',
                       'origin', 'bb', 'f3', '4b', '72', '88', '46', '08']
    if ignore_files is None:
        ignore_files = ['*.pyc', '__init__.py', '.DS_Store', '*.yaml', '*.json', '*.txt', '*.md', '*.csv', '*.png',
                        '*.jpg', '.idea', '*.git', '*.gitignore', '*.pylintrc', '.ipynb', '*.ipynb', '*.pkl',
                        '*.pickle', '*code_summary.py*', '*scratch*', '*test*']
    filtered_files = []
    for root, _, files in os.walk(path):
        if os.path.basename(root) in ignore_dirs:
            continue
        for file in files:
            filepath = os.path.join(root, file)
            if include and not any(fnmatch.fnmatch(file, pattern) for pattern in include):
                continue
            if exclude and any(fnmatch.fnmatch(file, pattern) for pattern in exclude):
                continue
            if any(fnmatch.fnmatch(file, pattern) for pattern in ignore_files):
                continue
            filtered_files.append(filepath)
    return filtered_files


def copy_directory_tree(path):
    tree = ''
    ignore_dirs = {'__pycache__', '.pytest_cache'}
    ignore_files = ['*.pyc', '__init__.py', '.DS_Store', '*.yaml', '*.json', '*.txt', '*.md', '*.csv', '*.png',
                    '*.jpg', '.idea', '*.git', '*.gitignore', '*.pylintrc', '.ipynb', '*.ipynb', '*.pkl', '*.pickle',
                    '*code_summary.py*', '*scratch*', '*test*']

    for root, dirs, files in os.walk(path):
        # Remove hidden directories and ignore_dirs from the list of directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ignore_dirs]

        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * level
        dir_name = os.path.basename(root)
        tree += f"{indent}{dir_name}/\n"
        subindent = ' ' * 4 * (level + 1)
        for file in files:
            if any(fnmatch.fnmatch(file, pat) for pat in ignore_files):
                continue
            tree += f"{subindent}{file}\n"
    pyperclip.copy(tree)
    return tree


def extract_py_files(tree_str):
    lines = tree_str.strip().split('\n')
    py_files = []
    for line in lines:
        if line.endswith('.py'):
            py_files.append(line.strip())
    return py_files


def read_multiline_input(prompt):
    print(prompt)
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    return '\n'.join(lines)
