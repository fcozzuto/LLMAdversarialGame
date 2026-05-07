def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves = [(dx, dy) for dx, dy in moves if in_bounds(sx + dx, sy + dy) and (sx + dx, sy + dy) not in blocked]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a resource where we are predicted to arrive no later than opponent; break ties by advantage then proximity.
    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = r[0], r[1]
        if not (isinstance(tx, int) and isinstance(ty, int) and in_bounds(tx, ty) and (tx, ty) not in blocked):
            continue
        myd = manh(sx, sy, tx, ty)
        opd = manh(ox, oy, tx, ty)
        # advantage > 0 means we likely win; prefer larger advantage, then smaller myd
        key = (opd - myd, -myd, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        # Fall back: go toward nearest non-blocked corner (deterministic).
        tx, ty = (w - 1, h - 1) if (sx + sy) % 2 == 0 else (0, 0)
    else:
        tx, ty = best

    # Move one step to reduce distance to chosen target, with secondary tie-break: maximize opponent distance.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        myd = manh(nx, ny, tx, ty)
        opd = manh(ox, oy, tx, ty)
        # Also discourage stepping into positions closer for opponent: compare their relative advantage if they contest same target.
        adv = opd - myd
        candidates.append(((adv, -myd, -manh(ox, oy, nx, ny), dx, dy), (dx, dy)))

    candidates.sort(reverse=True)
    return candidates[0][1]