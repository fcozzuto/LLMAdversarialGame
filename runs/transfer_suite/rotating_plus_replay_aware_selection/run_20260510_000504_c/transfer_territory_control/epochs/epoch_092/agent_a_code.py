def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = list(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_name = observation.get("self_name", "agent_a")
    opponent_name = observation.get("opponent_name", "agent_b")
    scores = observation.get("scores") or {}
    my_score = float(scores.get(self_name, 0.0) or 0.0)
    op_score = float(scores.get(opponent_name, 0.0) or 0.0)
    my_territory = set(map(tuple, observation.get("self_territory") or []))
    op_territory = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    aggressive = my_score < op_score

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        score = 0.0

        # Immediate value: claim/capture
        if (nx, ny) in unclaimed:
            score += 120.0
        if (nx, ny) in op_territory:
            score += 180.0 if aggressive else 140.0

        # Prefer moving outward from own area (expand), but stay away from obstacles already handled
        if (nx, ny) in my_territory:
            score -= 8.0

        # Avoid stepping adjacent to opponent if we're ahead; if behind, push toward them
        dpo = md(nx, ny, ox, oy)
        score += (-6.0 * dpo) if aggressive else (2.0 * dpo)

        # Resource attraction (if any)
        if resources:
            dr = min(md(nx, ny, rx, ry) for rx, ry in resources)
            score += 40.0 / (1.0 + dr)

        # Centralization to reduce edge trapping (territory control)
        score += -0.3 * (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))

        # Deterministic tie-break: lexicographic by move
        key = (-score, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]