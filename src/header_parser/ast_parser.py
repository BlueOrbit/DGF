# import libclang
# from libclang import cindex
import json
import os

import clang.cindex as cindex  # 这行关键

# 配置 libclang 路径
cindex.Config.set_library_file("/usr/lib/llvm-14/lib/libclang.so.1")



class ASTParser:
    def __init__(self, include_dirs=[]):
        self.include_dirs = include_dirs

    def parse(self, header_file):
        index = cindex.Index.create()
        args = ['-I' + inc for inc in self.include_dirs]
        tu = index.parse(header_file, args=args)
        return tu

    def extract(self, tu):
        functions, structs, typedefs, enums = [], [], [], []
        for node in tu.cursor.get_children():
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
