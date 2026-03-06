import os

import clang.cindex as cindex

_LIBCLANG_PATH = os.getenv("LIBCLANG_PATH")
if _LIBCLANG_PATH and not cindex.Config.loaded:
    cindex.Config.set_library_file(_LIBCLANG_PATH)



class ASTParser:
    def __init__(self, include_dirs=None):
        self.include_dirs = include_dirs or []

    def parse(self, header_file):
        index = cindex.Index.create()
        args = ['-I' + inc for inc in self.include_dirs]
        tu = index.parse(header_file, args=args)
        return tu

    def extract(self, tu, target_header=None):
        functions, structs, typedefs, enums = [], [], [], []
        target_header_path = os.path.abspath(target_header) if target_header else None
        for node in tu.cursor.get_children():
            if target_header_path and not _is_node_from_target_header(node, target_header_path):
                continue
            kind = node.kind
            if kind == cindex.CursorKind.FUNCTION_DECL:
                functions.append(self.extract_function(node))
            elif kind == cindex.CursorKind.STRUCT_DECL:
                structs.append(self.extract_struct(node))
            elif kind == cindex.CursorKind.TYPEDEF_DECL:
                typedefs.append(self.extract_typedef(node))
            elif kind == cindex.CursorKind.ENUM_DECL:
                enums.append(self.extract_enum(node))
        return {
            "functions": functions,
            "structs": structs,
            "typedefs": typedefs,
            "enums": enums
        }

    def extract_function(self, node):
        params = []
        for arg in node.get_arguments():
            params.append({
                "name": arg.spelling,
                "type": arg.type.spelling
            })
        return {
            "name": node.spelling,
            "result_type": node.result_type.spelling,
            "parameters": params
        }

    def extract_struct(self, node):
        fields = []
        for field in node.get_children():
            if field.kind == cindex.CursorKind.FIELD_DECL:
                fields.append({
                    "name": field.spelling,
                    "type": field.type.spelling
                })
        return {
            "name": node.spelling,
            "fields": fields
        }

    def extract_typedef(self, node):
        return {
            "name": node.spelling,
            "underlying_type": node.underlying_typedef_type.spelling
        }

    def extract_enum(self, node):
        constants = []
        for c in node.get_children():
            if c.kind == cindex.CursorKind.ENUM_CONSTANT_DECL:
                constants.append({
                    "name": c.spelling,
                    "value": c.enum_value
                })
        return {
            "name": node.spelling,
            "constants": constants
        }


def _is_node_from_target_header(node, target_header_path):
    location_file = getattr(getattr(node, "location", None), "file", None)
    if location_file is None:
        return False
    try:
        node_file_path = os.path.abspath(str(location_file))
    except Exception:
        return False
    return node_file_path == target_header_path
