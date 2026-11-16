from standards.constants import Language
from standards.suppressions import Suppression, count_suppressions


def test_python() -> None:
    source = """
from typing import Any
def f(a: Any) -> int:  # type: ignore[misc]
    return a  # noqa: E501
"""
    counts = count_suppressions(Language.PYTHON, source)
    assert counts == {
        Suppression.PY_ANY: 1,
        Suppression.PY_TYPE_IGNORE: 1,
        Suppression.PY_NOQA: 1,
    }


def test_typescript() -> None:
    source = """
// @ts-nocheck
// eslint-disable-next-line no-console
const a: any = 1;
"""
    counts = count_suppressions(Language.TYPESCRIPT, source)
    assert counts == {
        Suppression.TS_NOCHECK: 1,
        Suppression.ESLINT_DISABLE: 1,
        Suppression.TS_ANY: 1,
    }


def test_csharp() -> None:
    source = """
#pragma warning disable CS0168
class K {
  [SuppressMessage("a", "b")]
  void M() {}
}
#pragma warning restore CS0168
"""
    counts = count_suppressions(Language.CSHARP, source)
    assert counts == {Suppression.CS_PRAGMA: 1, Suppression.CS_SUPPRESS_MESSAGE: 1}


def test_reasoned_allow_comment_exempts_its_line_and_the_next() -> None:
    source = """
from typing import Any
x: Any = 1  # allow-suppression: third-party callback, untyped upstream
# allow-suppression: same, for the next line
y: Any = 2
z: Any = 3
"""
    assert count_suppressions(Language.PYTHON, source) == {Suppression.PY_ANY: 1}


def test_allow_comment_without_a_reason_exempts_nothing() -> None:
    source = "// allow-suppression:\nconst a: any = 1; // @ts-ignore\n"
    counts = count_suppressions(Language.TYPESCRIPT, source)
    assert counts == {Suppression.TS_ANY: 1, Suppression.TS_IGNORE: 1}
