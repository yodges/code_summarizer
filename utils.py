import fnmatch
import os
from pathlib import Path

import nbformat as nbf
import pyperclip


def write_to_file(output_file, content, is_notebook=False, join_with_newline=False):
    # Create the directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to the file (overwrite if it exists)
    with output_path.open('w') as f:
        if is_notebook:
            nbf.write(content, f)
        elif join_with_newline:
            f.write('\n'.join(content))
        else:
            f.write(content)


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
