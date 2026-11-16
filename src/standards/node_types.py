"""tree-sitter node type names the checks look for, per grammar."""

from __future__ import annotations

from enum import StrEnum

STATEMENT_SUFFIX = "_statement"
ANONYMOUS = "<anonymous>"


class Common(StrEnum):
    """Node types with the same name in more than one grammar."""

    COMMENT = "comment"
    CLASS_DECLARATION = "class_declaration"
    VARIABLE_DECLARATOR = "variable_declarator"


class SyntaxField(StrEnum):
    """tree-sitter field names, the same in every grammar."""

    NAME = "name"
    KEY = "key"
    LEFT = "left"


class Py(StrEnum):
    """tree-sitter-python."""

    FUNCTION = "function_definition"
    CLASS = "class_definition"
    IDENTIFIER = "identifier"
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
    PREDEFINED_TYPE = "predefined_type"


class TsToken(StrEnum):
    """Tokens of TypeScript and JavaScript."""

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
    PRAGMA = "preproc_pragma"
    ATTRIBUTE = "attribute"


class CsToken(StrEnum):
    """Tokens of C#."""

    WARNING = "warning"
    DISABLE = "disable"
    SUPPRESS_MESSAGE = "SuppressMessage"
    SUPPRESS_MESSAGE_ATTRIBUTE = "SuppressMessageAttribute"
