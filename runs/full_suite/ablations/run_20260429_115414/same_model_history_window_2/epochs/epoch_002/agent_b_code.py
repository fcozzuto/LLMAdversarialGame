def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def sgn(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if not resources:
        # Go to the quadrant farthest from opponent (deterministic)
        dx = sgn(w - 1 - x - (ox - 0))
        dy = sgn(h - 1 - y - (oy - 0))
        return [dx, dy]

    # Pick a resource that we can contest: maximize (opponent_dist - self_dist), tie-break by self_dist then lex.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist2(x, y, rx, ry)
        od = dist2(ox, oy, rx, ry)
        # Key: first maximize gap, then smaller self distance, then stable tie-break on coordinates
        key = (-(od - sd), sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    step_dx, step_dy = sgn(tx - x), sgn(ty - y)

    # Evaluate candidate moves with deterministic scoring
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                candidates.append((0, 0))
            elif abs(dx) + abs(dy) <= 2:
                candidates.append((dx, dy))
    # Filter to in-bounds and not into obstacles
    cand2 = []
    for dx, dy in candidates:
        nx, ny = x + dx, y + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            cand2.append((dx, dy))
    if not cand2:
        return [0, 0]

    # Scoring: move toward target, discourage moving closer to opponent, prefer positions with nearby resources.
    scored = []
    for dx, dy in cand2:
        nx, ny = x + dx, y + dy
        to_t = dist2(nx, ny, tx, ty)
        opp = dist2(nx, ny, ox, oy)
        # nearest resource proximity (small deterministic lookahead)
        near = 10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = dist2(nx, ny, rx, ry)
            if d < near:
                near = d
        # Prefer exact step direction when useful
        dir_align = -(abs(dx - step_dx) + abs(dy - step_dy))
        gap = dist2(ox, oy, tx, ty) - dist2(nx, ny, tx, ty)  # positive if we get closer relative to opponent
        val = (gap * 1000) - to_t + (opp * 0.001) - near * 0.0005 + dir_align
        # deterministic tie-break
        scored.append((-(val), dx, dy))
    scored.sort()
    _, dx, dy = scored[0]
    return [dx, dy]