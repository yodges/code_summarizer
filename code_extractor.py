import ast


class CodeExtractor(ast.NodeVisitor):
    def __init__(self, include_classes=None, include_methods=None, exclude_classes=None, exclude_methods=None):
        """Initialize code extractor with filtering options."""
        self.include_classes = include_classes or set()
        self.include_methods = include_methods or set()
        self.exclude_classes = exclude_classes or set()
        self.exclude_methods = exclude_methods or set()
        self.docstrings = []
        self.code_blocks = []
        self.docstring_blocks = []
        self.parent = None

    def is_class_included(self, class_name):
        """Check if a class should be included based on filtering options."""
        return (
                not self.include_classes or class_name in self.include_classes) \
            and class_name not in self.exclude_classes

    def is_method_included(self, method_name):
        """Check if a method should be included based on filtering options."""
        return (
                not self.include_methods or method_name in self.include_methods) \
            and method_name not in self.exclude_methods

    def remove_docstrings(self, body):
        """Remove docstrings from the body of a method or class."""
        if isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Str):
            self.docstrings.append(body[0].value.s)
            body.pop(0)
        else:
            self.docstrings.append('')

    def store_docstring(self, node):
        """Store the docstring of a class or method."""
        docstring = ast.get_docstring(node)
        if isinstance(node, ast.ClassDef):
            name = node.name
        elif isinstance(node, ast.FunctionDef):
            name = node.name
        else:
            name = None

        if docstring:
            self.docstrings.append(docstring)
            self.docstring_blocks.append((name, docstring))
        else:
            self.docstrings.append(None)
            self.docstring_blocks.append((name, None))

    @staticmethod
    def extract_method_definitions(method):
        """Extract method name and arguments from method definition."""
        method_name = method.name
        method_args = []
        for arg in method.args.args:
            arg_name = arg.arg
            arg_type = ast.unparse(arg.annotation).strip() if arg.annotation else None
            method_args.append(f"{arg_name}: {arg_type}" if arg_type else arg_name)
        method_args_str = ', '.join(method_args)
        return method_name, method_args_str

    @staticmethod
    def extract_decorators(decorator_list, indent_level=0):
        decorators = '\n'.join([f'{" " * 4 * indent_level}@{ast.unparse(d).strip()}' for d in decorator_list])
        return f'{decorators}\n' if decorators else ''

    @staticmethod
    def extract_code_block(body):
        code_block = ast.unparse(body)
        return '\n'.join(['    ' + line if line.strip() else line for line in code_block.splitlines()])

    @staticmethod
    def indent_code_block(code, level):
        return '\n'.join(['    ' * level + line if line.strip() else line for line in code.splitlines()])

    def visit_ClassDef(self, node):
        """Visit class definition and extract relevant code and docstrings."""
        if self.is_class_included(node.name):
            self.store_docstring(node)
            class_decorators = self.extract_decorators(node.decorator_list)
            self.remove_docstrings(node.body)
            class_code_block = f'{class_decorators}class {node.name}:'
            self.code_blocks.append(class_code_block)
            for method in node.body:
                if isinstance(method, ast.FunctionDef):
                    if self.is_method_included(method.name):
                        if method.name == '__init__' and len(method.body) == 1 and isinstance(method.body[0], ast.Pass):
                            continue
                        self.store_docstring(method)
                        decorators = self.extract_decorators(method.decorator_list, indent_level=1)
                        self.remove_docstrings(method.body)
                        (method_name, method_args_str) = self.extract_method_definitions(method)
                        method_body = self.indent_code_block(self.extract_code_block(method.body), 1)
                        method_code_block = f'{decorators}    def {method_name}({method_args_str}):\n{method_body}\n'
                        self.code_blocks.append(method_code_block)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Visit function definition and extract relevant code and docstrings."""
        if isinstance(node.parent, ast.ClassDef):
            return
        if self.is_method_included(node.name):
            self.store_docstring(node)  # Store the function's docstring
            decorators = self.extract_decorators(node.decorator_list)
            self.remove_docstrings(node.body)
            (function_name, function_args_str) = self.extract_method_definitions(node)
            function_body = self.extract_code_block(node.body)
            function_code_block = f'{decorators}def {function_name}({function_args_str}):\n{function_body}\n'
            self.code_blocks.append(function_code_block)
        self.generic_visit(node)

    def generic_visit(self, node):
        """Visit all nodes in the AST and set the parent attribute."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        item.parent = node
                        self.visit(item)
            elif isinstance(value, ast.AST):
                value.parent = node
                self.visit(value)
