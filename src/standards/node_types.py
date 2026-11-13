"""tree-sitter node type names the checks look for, per grammar."""

from __future__ import annotations

from enum import StrEnum

STATEMENT_SUFFIX = "_statement"
ANONYMOUS = "<anonymous>"


class Common(StrEnum):
    """Node types with the same name in more than one grammar."""

    COMMENT = "comment"
    STRING = "string"
    ESCAPE = "escape_sequence"
    CLASS_DECLARATION = "class_declaration"
    VARIABLE_DECLARATOR = "variable_declarator"
    BINARY = "binary_expression"


class SyntaxField(StrEnum):
    """tree-sitter field names, the same in every grammar."""

    NAME = "name"
    KEY = "key"
    LEFT = "left"
    RIGHT = "right"
    VALUE = "value"
    OPERATOR = "operator"


class Keyword(StrEnum):
    """Keywords shared by TypeScript and C#."""

    CONST = "const"


class Py(StrEnum):
    """tree-sitter-python."""

    FUNCTION = "function_definition"
    CLASS = "class_definition"
    COMPARISON = "comparison_operator"
    STRING_CONTENT = "string_content"
    INTERPOLATION = "interpolation"
    TUPLE = "tuple"
    LIST = "list"
    SET = "set"
    CASE_PATTERN = "case_pattern"
    UNION_PATTERN = "union_pattern"
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
    CLASS_EXPRESSION = "class"
    ABSTRACT_CLASS = "abstract_class_declaration"
    PAIR = "pair"
    FIELD = "public_field_definition"
    ASSIGNMENT = "assignment_expression"
    UNARY = "unary_expression"
    STRING_FRAGMENT = "string_fragment"
    TEMPLATE = "template_string"
    TEMPLATE_SUBSTITUTION = "template_substitution"
    SWITCH_CASE = "switch_case"
    PREDEFINED_TYPE = "predefined_type"
    LEXICAL_DECLARATION = "lexical_declaration"
    EXPORT = "export_statement"
    PROGRAM = "program"
    ENUM_ASSIGNMENT = "enum_assignment"
    AS_EXPRESSION = "as_expression"
    OBJECT = "object"


class TsToken(StrEnum):
    """Tokens of TypeScript and JavaScript."""

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
    STRUCT = "struct_declaration"
    RECORD = "record_declaration"
    INTERFACE = "interface_declaration"
    PROPERTY = "property_declaration"
    STRING = "string_literal"
    STRING_CONTENT = "string_literal_content"
    VERBATIM = "verbatim_string_literal"
    RAW = "raw_string_literal"
    RAW_CONTENT = "raw_string_content"
    CONSTANT_PATTERN = "constant_pattern"
    FIELD = "field_declaration"
    MODIFIER = "modifier"
    VARIABLE_DECLARATION = "variable_declaration"
    PRAGMA = "preproc_pragma"
    ATTRIBUTE = "attribute"


class CsToken(StrEnum):
    """Tokens of C#."""

    STATIC = "static"
    READONLY = "readonly"
    WARNING = "warning"  # same-value: a C# pragma token, not an annotation level
    DISABLE = "disable"
    SUPPRESS_MESSAGE = "SuppressMessage"
    SUPPRESS_MESSAGE_ATTRIBUTE = "SuppressMessageAttribute"


EQUALITY_OPERATORS = frozenset({"==", "!=", "===", "!=="})
