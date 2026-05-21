from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from llm_grid_battle.llm import _generate_text, judge_text, load_env_files

from .code_validation import validate_code


@dataclass
class GenerationResult:
    raw_text: str
    code: str
    submitted_code: str = ""
    error: str | None = None
    validation_issues: list[str] = field(default_factory=list)
    repair_attempted: bool = False
    used_fallback: bool = False


def default_solver_code() -> str:
    return _builtin_nearest_neighbor_code()


def builtin_solver_code(name: str) -> str:
    normalized = name.strip().lower()
    if normalized in {"phase9_builtin_nearest_neighbor", "nearest_neighbor"}:
        return _builtin_nearest_neighbor_code()
    if normalized in {"phase9_builtin_destroy_repair", "destroy_repair"}:
        return _builtin_destroy_repair_code()
    raise KeyError(f"Unknown phase-9 builtin solver model: {name}")


def extract_code(text: str) -> str:
    source = (text or "").strip()
    marker = "def solve_cvrp"
    start = source.find(marker)
    if start != -1:
        return source[start:].strip().strip("`")
    return source.strip().strip("`")


def generate_code(
    *,
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    repair_invalid_submissions: bool = True,
    timeout: float = 120.0,
    max_non_empty_lines: int = 220,
    max_characters: int = 12000,
) -> GenerationResult:
    if provider == "builtin":
        code = builtin_solver_code(model)
        return GenerationResult(raw_text=code, code=code, submitted_code=code)

    text, error = _generate_text(
        provider=provider,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    if error:
        fallback = default_solver_code()
        return GenerationResult(
            raw_text="",
            code=fallback,
            submitted_code="",
            error=error,
            used_fallback=True,
        )

    code = extract_code(text)
    issues = validate_code(code, max_non_empty_lines=max_non_empty_lines, max_characters=max_characters)
    if not issues:
        return GenerationResult(raw_text=text, code=code, submitted_code=code)
    if not repair_invalid_submissions:
        return GenerationResult(
            raw_text=text,
            code=default_solver_code(),
            submitted_code=code,
            error=f"Initial submission invalid ({', '.join(issues)})",
            validation_issues=issues,
            used_fallback=True,
        )

    repaired_text, repair_error = _generate_text(
        provider=provider,
        model=model,
        system_prompt=system_prompt,
        user_prompt=_build_repair_prompt(code, issues),
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    combined_raw = f"{text}\n\n--- REPAIR ATTEMPT ---\n\n{repaired_text}" if repaired_text else text
    if repair_error:
        return GenerationResult(
            raw_text=combined_raw,
            code=default_solver_code(),
            submitted_code=code,
            error=f"Initial submission invalid ({', '.join(issues)}); repair call failed: {repair_error}",
            validation_issues=issues,
            repair_attempted=True,
            used_fallback=True,
        )
    repaired_code = extract_code(repaired_text)
    repaired_issues = validate_code(repaired_code, max_non_empty_lines=max_non_empty_lines, max_characters=max_characters)
    if repaired_issues:
        return GenerationResult(
            raw_text=combined_raw,
            code=default_solver_code(),
            submitted_code=repaired_code,
            error=(
                f"Initial submission invalid ({', '.join(issues)}); "
                f"repair submission invalid ({', '.join(repaired_issues)})"
            ),
            validation_issues=repaired_issues,
            repair_attempted=True,
            used_fallback=True,
        )
    return GenerationResult(
        raw_text=combined_raw,
        code=repaired_code,
        submitted_code=repaired_code,
        repair_attempted=True,
    )


def _build_repair_prompt(code: str, issues: list[str]) -> str:
    return "\n".join(
        [
            "Repair the Python CVRP solver below.",
            "Return only raw Python source code.",
            "The first line must be exactly: def solve_cvrp(instance):",
            "Do not use markdown fences.",
            "Do not use import statements of any kind.",
            "Return deterministic Python that produces a full CVRP solution as a list of routes.",
            "",
            "Validator feedback:",
            *[f"- {issue}" for issue in issues],
            "",
            "Previous invalid submission:",
            code,
        ]
    )


def _builtin_nearest_neighbor_code() -> str:
    return """def solve_cvrp(instance):
    depot = instance["depot_index"]
    customers = set(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    matrix = instance["distance_matrix"]
    routes = []
    while customers:
        route = []
        load = 0
        current = depot
        while True:
            feasible = [node for node in customers if load + demands[node] <= capacity]
            if not feasible:
                break
            nxt = min(feasible, key=lambda node: (matrix[current][node], demands[node], node))
            route.append(nxt)
            customers.remove(nxt)
            load += demands[nxt]
            current = nxt
        routes.append(route)
    return routes
"""


def _builtin_destroy_repair_code() -> str:
    return """def solve_cvrp(instance):
    depot = instance["depot_index"]
    customers = list(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    matrix = instance["distance_matrix"]
    descriptors = instance["descriptors"]

    def route_cost(route):
        if not route:
            return 0
        cost = matrix[depot][route[0]]
        for left, right in zip(route, route[1:]):
            cost += matrix[left][right]
        cost += matrix[route[-1]][depot]
        return cost

    def greedy_seed(order):
        remaining = set(order)
        built = []
        while remaining:
            route = []
            load = 0
            current = depot
            while True:
                feasible = [node for node in remaining if load + demands[node] <= capacity]
                if not feasible:
                    break
                nxt = min(feasible, key=lambda node: (matrix[current][node], -demands[node], node))
                route.append(nxt)
                remaining.remove(nxt)
                load += demands[nxt]
                current = nxt
            built.append(route)
        return built

    def best_insertion(route, customer):
        if not route:
            return 2 * matrix[depot][customer], 0
        best_delta = None
        best_pos = 0
        previous = depot
        for pos, nxt in enumerate(route):
            delta = matrix[previous][customer] + matrix[customer][nxt] - matrix[previous][nxt]
            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_pos = pos
            previous = nxt
        tail = matrix[previous][customer] + matrix[customer][depot] - matrix[previous][depot]
        if best_delta is None or tail < best_delta:
            return tail, len(route)
        return best_delta, best_pos

    def repair(routes):
        remaining = []
        kept = []
        for route in routes:
            load = 0
            compact = []
            for node in route:
                if node in compact or node in remaining:
                    continue
                if load + demands[node] > capacity:
                    remaining.append(node)
                else:
                    compact.append(node)
                    load += demands[node]
            if compact:
                kept.append(compact)
        missing = [node for node in customers if all(node not in route for route in kept) and node not in remaining]
        remaining.extend(missing)
        while remaining:
            customer = remaining.pop(0)
            choices = []
            for idx, route in enumerate(kept):
                if sum(demands[node] for node in route) + demands[customer] > capacity:
                    continue
                delta, pos = best_insertion(route, customer)
                choices.append((delta, idx, pos))
            if choices:
                choices.sort()
                _, idx, pos = choices[0]
                kept[idx].insert(pos, customer)
            else:
                kept.append([customer])
        return kept

    ordered = sorted(customers, key=lambda node: (matrix[depot][node], node))
    if descriptors.get("nearest_neighbor_trap_score", 0.0) >= 0.18 or descriptors.get("corridor_score", 0.0) >= 0.4:
        ordered = sorted(customers, key=lambda node: (-matrix[depot][node], -demands[node], node))
    best_routes = greedy_seed(ordered)
    best_cost = sum(route_cost(route) for route in best_routes)
    for _ in range(2):
        rebuilt = []
        leftovers = []
        for route in best_routes:
            if len(route) <= 4:
                rebuilt.append(list(route))
                continue
            cut = max(1, len(route) // 3)
            leftovers.extend(route[-cut:])
            rebuilt.append(route[:-cut])
        candidate = repair(rebuilt + [[node] for node in leftovers])
        candidate_cost = sum(route_cost(route) for route in candidate)
        if candidate_cost < best_cost:
            best_routes = candidate
            best_cost = candidate_cost
    return best_routes
"""
