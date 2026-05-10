def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    unclaimed = observation.get("unclaimed_cells", []) or []
    opp_terr = observation.get("opponent_territory", []) or []
    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target: nearest unclaimed that maximizes distance from opponent; fallback: nearest opponent territory; fallback: stay near opponent
    if unclaimed:
        tx, ty = min(
            unclaimed,
            key=lambda p: (md(sx, sy, p[0], p[1]) - 0.35 * md(ox, oy, p[0], p[1]))
        )
    elif opp_terr:
        tx, ty = min(
            opp_terr,
            key=lambda p: (md(sx, sy, p[0], p[1]) - 0.15 * md(ox, oy, p[0], p[1]))
        )
    else:
        tx, ty = ox, oy

    # Move score: prefer decreasing distance to target; discourage stepping toward opponent if it risks being flipped back
    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dt = md(nx, ny, tx, ty)
        do = md(nx, ny, ox, oy)
        # If landing on opponent territory, flipping can help; reward being closer to target and farther from opponent simultaneously
        on_opp = any((nx == ex and ny == ey) for ex, ey in opp_terr) if opp_terr else False
        score = -dt + 0.10 * do + (0.8 if on_opp else 0.0)
        # Prefer exploration vs being stuck
        if dx == 0 and dy == 0:
            score -= 0.08
        # Deterministic tie-breaker: fixed ordering already; keep earliest best
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]