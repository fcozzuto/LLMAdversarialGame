def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", [])
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells", None)
    if not unclaimed:
        unclaimed = []
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in blocked:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    targets = []
    if unclaimed:
        targets = unclaimed
    else:
        targets = [(ox, oy)]

    best = None
    best_key = None
    for dx, dy, nx, ny in candidates:
        # Prefer reducing distance to nearest target; tie-break deterministically.
        md = None
        for tx, ty in targets:
            d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            if md is None or d < md:
                md = d
        if md is None:
            md = 0
        # Small deterministic preference to keep moves stable: diagonals first, then straight.
        diag = 1 if dx != 0 and dy != 0 else 0
        straight = 1 if (dx == 0) ^ (dy == 0) else 0
        key = (md, -diag, -straight, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best