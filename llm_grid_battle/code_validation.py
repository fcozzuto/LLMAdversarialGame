from __future__ import annotations

import ast

TARGET_NON_EMPTY_LINES = 60
MAX_NON_EMPTY_LINES = 80
TARGET_CHARACTERS = 4000
MAX_CHARACTERS = 4500


DISALLOWED_CALLS = {
    "__import__",
    "compile",
    "delattr",
    "eval",
    "exec",
    "getattr",
    "globals",
    "help",
    "input",
    "locals",
    "open",
    "setattr",
    "vars",
}


def count_non_empty_lines(code: str) -> int:
    return sum(1 for line in code.splitlines() if line.strip())


def _block_guarantees_return(statements: list[ast.stmt]) -> bool:
    for statement in statements:
        if _statement_guarantees_return(statement):
            return True
    return False


def _statement_guarantees_return(statement: ast.stmt) -> bool:
    if isinstance(statement, ast.Return):
        return True
    if isinstance(statement, ast.If):
        return bool(statement.body) and bool(statement.orelse) and _block_guarantees_return(statement.body) and _block_guarantees_return(statement.orelse)
    if isinstance(statement, (ast.With, ast.AsyncWith)):
        return _block_guarantees_return(statement.body)
    if isinstance(statement, ast.Try):
        handlers_return = bool(statement.handlers) and all(_block_guarantees_return(handler.body) for handler in statement.handlers)
        body_returns = _block_guarantees_return(statement.body)
        else_returns = _block_guarantees_return(statement.orelse) if statement.orelse else False
        if statement.finalbody and _block_guarantees_return(statement.finalbody):
            return True
        return body_returns and handlers_return and (else_returns if statement.orelse else True)
    if isinstance(statement, ast.Match):
        return bool(statement.cases) and all(_block_guarantees_return(case.body) for case in statement.cases)
    return False


def validate_code(code: str) -> list[str]:
    issues: list[str] = []
    char_count = len(code)
    if char_count > MAX_CHARACTERS:
        issues.append(f"too_many_characters:{char_count}")
    non_empty_lines = count_non_empty_lines(code)
    if non_empty_lines > MAX_NON_EMPTY_LINES:
        issues.append(f"too_many_non_empty_lines:{non_empty_lines}")
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        issues.append(f"syntax_error:{exc.msg}")
        return sorted(set(issues))

    entrypoint: ast.FunctionDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            issues.append("imports_not_allowed")
        elif isinstance(node, ast.Attribute) and str(node.attr).startswith("__"):
            issues.append("dunder_attribute_not_allowed")
        elif isinstance(node, ast.Name) and str(node.id).startswith("__"):
            issues.append("dunder_name_not_allowed")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in DISALLOWED_CALLS:
                issues.append(f"disallowed_call:{node.func.id}")
        elif isinstance(node, ast.FunctionDef) and node.name == "choose_move":
            entrypoint = node
    if entrypoint is None:
        issues.append("missing_choose_move")
    elif not _block_guarantees_return(entrypoint.body):
        issues.append("entrypoint_may_fall_through")
    return sorted(set(issues))
