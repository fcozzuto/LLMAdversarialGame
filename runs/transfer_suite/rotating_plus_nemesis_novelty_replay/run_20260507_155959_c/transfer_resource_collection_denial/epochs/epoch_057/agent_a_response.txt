def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if (sx, sy) in obs:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy  # diagonal allowed => Chebyshev
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Estimate race: pick resource where we arrive no later than opponent, maximizing margin.
    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ts = md(sx, sy, rx, ry)
        to = md(ox, oy, rx, ry)
        # Prefer steal (ts<=to). Otherwise deny: closest resource to opponent's arrival.
        # key: (steal_flag, margin, to, -ts)
        steal_flag = 1 if ts <= to else 0
        margin = (to - ts)
        key = (steal_flag, margin, to, -ts, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Greedy step toward target with obstacle-avoidance; tie-break toward blocking opponent line.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            dist_now = md(nx, ny, tx, ty)
            # Blocking tendency: move that also increases opponent distance to same target.
            opp_dist = md(ox, oy, tx, ty)
            opp_next = md(ox, oy, tx, ty)  # opponent move unknown; keep deterministic neutral
            # key: prefer smaller dist, then prefer larger improvement potential vs us (dist_now), then lexicographic
            moves.append(((0, -dist_now, -opp_dist, dx, dy), dist_now, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda z: z[0])
    return [moves[0][2], moves[0][3]]