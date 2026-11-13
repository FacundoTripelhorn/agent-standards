from standards.constants import Language
from standards.literals import constant_definitions, literal_comparisons


def values(language: Language, source: str) -> list[str]:
    return [u.value for u in literal_comparisons(language, source)]


def test_python_comparisons_membership_and_case() -> None:
    source = """
if a == "x" or a in ("y", "z") or a == "":
    pass
match a:
    case "q" | "r":
        pass
"""
    assert values(Language.PYTHON, source) == ["x", "y", "z", "q", "r"]


def test_python_idioms_are_exempt() -> None:
    source = """
import sys
if __name__ == "__main__":
    pass
if sys.platform == "win32":
    pass
"""
    assert values(Language.PYTHON, source) == []


def test_typescript_equality_switch_and_exemptions() -> None:
    source = """
if (a === "x" || a != 'y') {}
switch (a) { case "z": break; }
if (typeof a === "string") {}
if (process.platform === "win32") {}
if (a === `t${b}`) {}
if (a === `u`) {}
"""
    assert values(Language.TYPESCRIPT, source) == ["x", "y", "z", "u"]


def test_csharp_equality_case_arms_and_is() -> None:
    source = """
class K { int M(string s) {
  if (s == "x") return 1;
  switch (s) { case "y": return 2; }
  var r = s switch { "z" => 3, _ => 0 };
  if (s is "w") return 4;
  if (s == $"{s}") return 5;
  return 0; } }
"""
    assert values(Language.CSHARP, source) == ["x", "y", "z", "w"]


def test_python_constants_with_owner_and_marker() -> None:
    source = """
X = "a"
# same-value: a different concept
Y = "a"
lower = "b"
class S:
    OK = "ok"
def f():
    LOCAL = "c"
"""
    found = [
        (d.name, d.value, d.marked)
        for d in constant_definitions(Language.PYTHON, source)
    ]
    assert found == [("X", "a", False), ("Y", "a", True), ("S.OK", "ok", False)]


def test_typescript_constants() -> None:
    source = """
export const X = "a";
const M = { A: "b" } as const;
enum E { C = "c" }
let notConst = "d";
function f() { const inner = "e"; }
"""
    found = [
        (d.name, d.value) for d in constant_definitions(Language.TYPESCRIPT, source)
    ]
    assert found == [("X", "a"), ("M.A", "b"), ("C", "c")]


def test_csharp_constants() -> None:
    source = """
class K {
  const string X = "a";
  static readonly string Y = "b";
  readonly string notConstant = "c";
}
"""
    found = [(d.name, d.value) for d in constant_definitions(Language.CSHARP, source)]
    assert found == [("X", "a"), ("Y", "b")]
