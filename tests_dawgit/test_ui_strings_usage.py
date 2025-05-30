import ast
from pathlib import Path
import pytest

SOURCE_DIR = Path(__file__).parent.parent
EXCLUDE = {"ui_strings.py", "__init__.py"}

def extract_ui_strings_from_file(file_path):
    """Returns list of string literals used in UI element constructors."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    issues = []

    class StringVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "QLabel", "QPushButton", "QCheckBox", "QMessageBox", "setText", "setToolTip"
            }:
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        issues.append((node.lineno, arg.value))
            self.generic_visit(node)

    StringVisitor().visit(tree)
    return issues

@pytest.mark.parametrize("file_path", [
    str(p) for p in (SOURCE_DIR / "daw_git_gui.py").parent.glob("*.py")
    if p.name not in EXCLUDE
])
def test_no_hardcoded_ui_strings(file_path):
    issues = extract_ui_strings_from_file(Path(file_path))
    assert not issues, f"Hardcoded strings found in {file_path}:\n" + "\n".join(
        f"Line {line}: '{string}'" for line, string in issues
    )
