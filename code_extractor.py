import ast
import fnmatch
import os

import pyperclip


class CodeExtractor(ast.NodeVisitor):
    def __init__(self, include_classes=None, include_methods=None, exclude_classes=None, exclude_methods=None):
        self.include_classes = include_classes or set()
        self.include_methods = include_methods or set()
        self.exclude_classes = exclude_classes or set()
        self.exclude_methods = exclude_methods or set()
        self.code_blocks = []
        self.parent = None

    def is_class_included(self, class_name):
        return (
                not self.include_classes or class_name in self.include_classes) \
            and class_name not in self.exclude_classes

    def is_method_included(self, method_name):
        return (
                not self.include_methods or method_name in self.include_methods) \
            and method_name not in self.exclude_methods

    @staticmethod
    def remove_docstrings(body):
        if isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Str):
            body.pop(0)

    @staticmethod
    def extract_method_definitions(method):
        method_name = method.name
        method_args = []
        for arg in method.args.args:
            arg_name = arg.arg
            arg_type = ast.unparse(arg.annotation).strip() if arg.annotation else None
            method_args.append(f"{arg_name}: {arg_type}" if arg_type else arg_name)
        method_args_str = ', '.join(method_args)
        return method_name, method_args_str

    @staticmethod
    def extract_decorators(decorator_list):
        decorators = '\n'.join([f"@{ast.unparse(d).strip()}" for d in decorator_list])
        return f"{decorators}\n" if decorators else ""

    @staticmethod
    def extract_code_block(body):
        code_block = ast.unparse(body)
        return '\n'.join(['    ' + line if line.strip() else line for line in code_block.splitlines()])

    def visit_ClassDef(self, node):
        if self.is_class_included(node.name):
            class_decorators = self.extract_decorators(node.decorator_list)
            self.remove_docstrings(node.body)
            methods = []
            for method in node.body:
                if isinstance(method, ast.FunctionDef):
                    if self.is_method_included(method.name):
                        decorators = self.extract_decorators(method.decorator_list)
                        self.remove_docstrings(method.body)
                        method_name, method_args_str = self.extract_method_definitions(method)
                        method_body = self.extract_code_block(method.body)
                        methods.append(f"{decorators}def {method_name}({method_args_str}):\n{method_body}\n\n")
            methods_str = '\n'.join(
                ['    ' + line if line.strip() else line for method in methods for line in method.splitlines()])
            self.code_blocks.append(f"{class_decorators}class {node.name}:\n{methods_str}")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if isinstance(node.parent, ast.ClassDef):
            return

        if self.is_method_included(node.name):
            decorators = self.extract_decorators(node.decorator_list)
            self.remove_docstrings(node.body)

            function_name, function_args_str = self.extract_method_definitions(node)
            function_body = self.extract_code_block(node.body)
            self.code_blocks.append(f"{decorators}def {function_name}({function_args_str}):\n{function_body}\n")

        self.generic_visit(node)

    def generic_visit(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        item.parent = node
                        self.visit(item)
            elif isinstance(value, ast.AST):
                value.parent = node
                self.visit(value)


def extract_code(filenames, output_file, include_classes=None, include_methods=None, exclude_classes=None,
                 exclude_methods=None):
    desired_code_blocks = []

    for filename in filenames:
        with open(filename, 'r') as f:
            code = f.read()
        ast_tree = ast.parse(code)
        ast.fix_missing_locations(ast_tree)

        extractor = CodeExtractor(include_classes, include_methods, exclude_classes, exclude_methods)
        extractor.visit(ast_tree)
        desired_code = '\n'.join(extractor.code_blocks)

        if desired_code:
            file_name_only = os.path.basename(filename)
            desired_code_blocks.append(f"# {file_name_only}:\n{desired_code}\n")

    with open(output_file, 'w') as f:
        f.write('\n'.join(desired_code_blocks))


def filter_files(path, include=None, exclude=None, ignore_dirs=None, ignore_files=None):
    if ignore_dirs is None:
        ignore_dirs = ['__pycache__', '.pytest_cache', 'v', 'cache']
    if ignore_files is None:
        ignore_files = ['*.pyc', '__init__.py', '.DS_Store', '*.yaml', '*.json', '*.txt', '*.md', '*.csv', '*.png',
                        '*.jpg']
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
    ignore_dirs = ['__pycache__', '.pytest_cache', 'v', 'cache']
    ignore_files = ['*.pyc', '__init__.py', '.DS_Store', '*.yaml', '*.json', '*.txt', '*.md', '*.csv', '*.png',
                    '*.jpg']
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * level
        dir_name = os.path.basename(root)
        if any(dir_name.startswith(d) for d in ignore_dirs):
            continue
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


if __name__ == "__main__":
    output_file = '/Users/mhodges/PycharmProjects/crypto_twitter_analytics' \
                  '/GCPApps/toto/scratch/extracted_code_summary.py'

    source_directory = input("Enter the source directory: ")
    tree_string = copy_directory_tree(source_directory)

    # Use the read_multiline_input function to read the directory tree string.
    tree_string_input = read_multiline_input(
        "Paste the directory tree string to filter directory code (Press enter twice to finish):")
    if not tree_string_input:
        tree_string_input = tree_string

    include = extract_py_files(tree_string_input)
    print("Extracting:", include)

    filtered_files = filter_files(source_directory, include=include)

    extract_code(filtered_files, output_file)
