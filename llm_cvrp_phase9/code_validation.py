from __future__ import annotations

import ast


TARGET_NON_EMPTY_LINES = 220
TARGET_CHARACTERS = 12000

BANNED_NAMES = {
    "__import__",
    "eval",
    "exec",
    "open",
    "compile",
    "globals",
    "locals",
    "input",
    "help",
    "getattr",
    "setattr",
    "delattr",
}


def count_non_empty_lines(code: str) -> int:
    return sum(1 for line in code.splitlines() if line.strip())


def validate_code(
    code: str,
    *,
    max_non_empty_lines: int = TARGET_NON_EMPTY_LINES,
    max_characters: int = TARGET_CHARACTERS,
) -> list[str]:
    issues: list[str] = []
    if not code.strip():
        return ["submission was empty"]
    if count_non_empty_lines(code) > max_non_empty_lines:
        issues.append(f"submission exceeded {max_non_empty_lines} non-empty lines")
    if len(code) > max_characters:
        issues.append(f"submission exceeded {max_characters} characters")
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        issues.append(f"syntax error: {exc.msg}")
        return issues

    solver_defs = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "solve_cvrp"
    ]
    if not solver_defs:
        issues.append("missing required function solve_cvrp(instance)")
    elif len(solver_defs) > 1:
        issues.append("solve_cvrp is defined more than once")
    else:
        solver = solver_defs[0]
        if len(solver.args.args) != 1 or solver.args.args[0].arg != "instance":
            issues.append("solve_cvrp must accept exactly one argument named instance")
        if not any(isinstance(node, ast.Return) for node in ast.walk(solver)):
            issues.append("solve_cvrp does not contain a return statement")

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            issues.append("import statements are not allowed")
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "__builtins__":
            issues.append("direct __builtins__ access is not allowed")
        elif isinstance(node, ast.Call):
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            if name in BANNED_NAMES:
                issues.append(f"call to banned builtin {name}()")
    return issues
