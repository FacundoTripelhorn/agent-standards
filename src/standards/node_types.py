"""tree-sitter node type names the checks look for, per grammar."""

from __future__ import annotations

from enum import StrEnum

STATEMENT_SUFFIX = "_statement"
ANONYMOUS = "<anonymous>"


class Py(StrEnum):
    """tree-sitter-python."""

    FUNCTION = "function_definition"
    CLASS = "class_definition"
    COMPARISON = "comparison_operator"
    STRING = "string"
    STRING_CONTENT = "string_content"
    ESCAPE = "escape_sequence"
    INTERPOLATION = "interpolation"
    TUPLE = "tuple"
    LIST = "list"
    SET = "set"
    CASE_PATTERN = "case_pattern"
    UNION_PATTERN = "union_pattern"
    COMMENT = "comment"
    IDENTIFIER = "identifier"
    ASSIGNMENT = "assignment"
    EXPRESSION_STATEMENT = "expression_statement"
    MODULE = "module"
    BLOCK = "block"
    IMPORT_FROM = "import_from_statement"
    ELIF = "elif_clause"
    ELSE = "else_clause"
    EXCEPT = "except_clause"
    FINALLY = "finally_clause"
    CASE = "case_clause"


class Ts(StrEnum):
    """tree-sitter-typescript and tree-sitter-javascript."""

    FUNCTION = "function_declaration"
    GENERATOR = "generator_function_declaration"
    FUNCTION_EXPRESSION = "function_expression"
    FUNCTION_LEGACY = "function"
    GENERATOR_EXPRESSION = "generator_function"
    ARROW = "arrow_function"
    METHOD = "method_definition"
    CLASS = "class_declaration"
    CLASS_EXPRESSION = "class"
    ABSTRACT_CLASS = "abstract_class_declaration"
    VARIABLE_DECLARATOR = "variable_declarator"
    PAIR = "pair"
    FIELD = "public_field_definition"
    ASSIGNMENT = "assignment_expression"
    BINARY = "binary_expression"
    UNARY = "unary_expression"
    STRING = "string"
    STRING_FRAGMENT = "string_fragment"
    ESCAPE = "escape_sequence"
    TEMPLATE = "template_string"
    TEMPLATE_SUBSTITUTION = "template_substitution"
    SWITCH_CASE = "switch_case"
    COMMENT = "comment"
    PREDEFINED_TYPE = "predefined_type"
    LEXICAL_DECLARATION = "lexical_declaration"
    EXPORT = "export_statement"
    PROGRAM = "program"
    ENUM_ASSIGNMENT = "enum_assignment"
    AS_EXPRESSION = "as_expression"
    OBJECT = "object"


class TsToken(StrEnum):
    """Tokens of TypeScript and JavaScript."""

    CONST = "const"
    TYPEOF = "typeof"
    ANY = "any"


class Cs(StrEnum):
    """tree-sitter-c-sharp."""

    METHOD = "method_declaration"
    CONSTRUCTOR = "constructor_declaration"
    DESTRUCTOR = "destructor_declaration"
    OPERATOR = "operator_declaration"
    CONVERSION = "conversion_operator_declaration"
    LOCAL_FUNCTION = "local_function_statement"
    ACCESSOR = "accessor_declaration"
    CLASS = "class_declaration"
    STRUCT = "struct_declaration"
    RECORD = "record_declaration"
    INTERFACE = "interface_declaration"
    PROPERTY = "property_declaration"
    BINARY = "binary_expression"
    STRING = "string_literal"
    STRING_CONTENT = "string_literal_content"
    ESCAPE = "escape_sequence"
    VERBATIM = "verbatim_string_literal"
    RAW = "raw_string_literal"
    RAW_CONTENT = "raw_string_content"
    CONSTANT_PATTERN = "constant_pattern"
    FIELD = "field_declaration"
    MODIFIER = "modifier"
    VARIABLE_DECLARATION = "variable_declaration"
    VARIABLE_DECLARATOR = "variable_declarator"
    PRAGMA = "preproc_pragma"
    ATTRIBUTE = "attribute"
    COMMENT = "comment"


class CsToken(StrEnum):
    """Tokens of C#."""

    CONST = "const"
    STATIC = "static"
    READONLY = "readonly"
    WARNING = "warning"
    DISABLE = "disable"
    SUPPRESS_MESSAGE = "SuppressMessage"
    SUPPRESS_MESSAGE_ATTRIBUTE = "SuppressMessageAttribute"


EQUALITY_OPERATORS = frozenset({"==", "!=", "===", "!=="})
