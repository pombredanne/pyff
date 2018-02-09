"""Functions for comparison of various Python entities"""

from ast import FunctionDef, parse, NodeVisitor, Module
from typing import cast
from collections import defaultdict
from pyff.pyfference import FunctionPyfference, ModulePyfference, FromImportPyfference

def _pyff_function_ast(first: FunctionDef, second: FunctionDef) -> FunctionPyfference:
    """Return differences between two Python function ASTs, or None if they are identical"""
    if first.name == second.name:
        return None

    return FunctionPyfference(names=(first.name, second.name))

def _pyff_from_imports(first_ast: Module, second_ast: Module) -> FromImportPyfference:
    """Return differences in `from X import Y` statements in two modules"""
    first_walker = ImportFromExtractor()
    second_walker = ImportFromExtractor()

    first_walker.visit(first_ast)
    second_walker.visit(second_ast)

    appeared = set(second_walker.modules.keys()) - set(first_walker.modules.keys())
    new = {}
    for module in appeared:
        new[module] = second_walker.modules[module]

    return FromImportPyfference(new) if new else None

def _pyff_modules(first_ast: Module, second_ast: Module) -> ModulePyfference:
    from_imports = _pyff_from_imports(first_ast, second_ast)

    return ModulePyfference(from_imports) if from_imports else None

class ImportFromExtractor(NodeVisitor):
    """Extracts information about `from x import y` statements"""
    def __init__(self):
        self.modules = defaultdict(set)
        super(ImportFromExtractor, self).__init__()

    def visit_ImportFrom(self, node): # pylint: disable=invalid-name
        """Save information about `from x import y` statements"""
        self.modules[node.module].update([node.name for node in node.names])

def pyff_function(first: str, second: str) -> FunctionPyfference:
    """Return differences between two Python functions, or None if they are identical"""
    first_ast = parse(first).body
    second_ast = parse(second).body

    if len(first_ast) != 1 or not isinstance(first_ast[0], FunctionDef):
        raise ValueError(f"First argument does not seem to be a single Python function: {first}")
    if len(second_ast) != 1 or not isinstance(second_ast[0], FunctionDef):
        raise ValueError(f"Second argument does not seem to be a single Python function: {second}")

    return _pyff_function_ast(cast(FunctionDef, first_ast[0]), cast(FunctionDef, second_ast[0]))

def pyff_module(first: str, second: str) -> ModulePyfference:
    """Return difference between two Python modules, or None if they are identical"""
    # pylint: disable=unused-variable
    first_ast = parse(first)
    second_ast = parse(second)
    return _pyff_modules(first_ast, second_ast)
