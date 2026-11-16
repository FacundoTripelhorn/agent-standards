from standards.constants import Language
from standards.metrics import file_size, function_sizes

PY = """
def f(a):
    if a:
        x = 1
    elif a > 2:
        x = 2
    else:
        x = 3
    return x
"""

TS = """
function f(a: number): number {
  // comment

  return a;
}
const g = (b: string) => b;
class K { m() { return 1 } }
"""

CS = """
class K {
  int M(string s) {
    // only a comment

    return 1;
  }
  int M(int s) { return 2; }
}
"""


def test_python_function_counts_statements_and_clauses() -> None:
    [fn] = function_sizes(Language.PYTHON, PY)
    # if + 2 assignments in branches + elif + else + 1 assignment + return
    assert (fn.key, fn.size) == ("f", 7)


def test_typescript_counts_every_line_and_names_arrow_functions() -> None:
    sizes = {f.key: f.size for f in function_sizes(Language.TYPESCRIPT, TS)}
    assert sizes == {"f": 5, "g": 1, "K.m": 1}


def test_csharp_counts_code_lines_and_numbers_overloads() -> None:
    sizes = {f.key: f.size for f in function_sizes(Language.CSHARP, CS)}
    assert sizes == {"K.M": 3, "K.M#2": 1}


def test_file_size_units() -> None:
    assert file_size(Language.TYPESCRIPT, TS) == 8
    # C# counts lines of code only: the comment and blank lines do not count.
    assert file_size(Language.CSHARP, CS) == 6
