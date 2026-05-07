def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    # Opponent position for denial pressure
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    candidates = []
    for r in resources:
        if not isinstance(r, (list, tuple)) or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if not isinstance(rx, int) or not isinstance(ry, int):
            continue
        if not (0 <= rx < w and 0 <= ry < h):
            continue
        if (rx, ry) in blocked:
            continue
        dme = cheb(sx, sy, rx, ry)
        dop = cheb(ox, oy, rx, ry)
        # Score: prefer nearer; if opponent is closer, strongly prefer denying
        gain = 0
        if dop < dme:
            gain = 1000 + (dme - dop)
        else:
            gain = dme
        candidates.append((gain, rx, ry, dme, dop))

    # Determine move from best target, with deterministic tie-breaking
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    if not candidates:
        # No visible resources: drift toward center to reduce distance variance
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            if d < bestd:
                bestd = d
                best_move = [dx, dy]
        return best_move

    candidates.sort(key=lambda t: (t[0], t[3], t[4], t[1], t[2]))
    _, tx, ty, _, _ = candidates[0]

    # Prefer stepping closer to target, but avoid obstacles; deterministic order handles ties
    bestd = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Small denial bias: if move increases opponent distance to target, it's slightly better
        dop = cheb(ox, oy, tx, ty)
        dop2 = cheb(ox, oy, tx, ty)  # unchanged (we don't predict opponent); keep deterministic
        _ = dop2
        if d < bestd:
            bestd = d
            best_move = [dx, dy]

    return best_move