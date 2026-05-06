def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if not legal(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if legal(sx + dx, sy + dy):
                    return [dx, dy]
        return [0, 0]

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position", None)
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if legal(x, y):
                    rpos.append((x, y))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if legal(x, y):
                rpos.append((x, y))

    if not rpos:
        return [0, 0]

    # Choose a resource where we have advantage; also prefer blocking the opponent's sweep lines.
    # Blocking heuristic: resources aligned with opponent (same x or same y) are higher priority.
    best = None
    best_key = None
    for x, y in rpos:
        d_ours = md(sx, sy, x, y)
        d_opp = md(ox, oy, x, y)
        advantage = d_opp - d_ours
        aligned = 1 if (x == ox or y == oy) else 0
        # Prefer closer targets among equal advantage; deterministic tie-break by coordinates.
        key = (advantage, aligned, -d_ours, -abs(sx - x) - abs(sy - y), -x, -y)
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    # Move to best immediate legal delta toward target while maintaining safety.
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Primary: reduce distance to target; Secondary: reduce alignment difference; Tertiary: avoid getting stuck.
        dnew = md(nx, ny, tx, ty)
        align_new = 1 if (nx == ox or ny == oy) else 0
        stuck_pen = 0 if (dx == 0 and dy == 0) else 1  # discourage staying still if equal
        mkey = (-dnew, -align_new, stuck_pen, nx, ny)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]