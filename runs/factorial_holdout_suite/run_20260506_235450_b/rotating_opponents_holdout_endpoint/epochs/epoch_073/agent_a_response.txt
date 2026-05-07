def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Target: maximize time-advantage; tie-break by smaller self distance then lexicographic.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, -rx, -ry)  # deterministic ordering
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Move choice: evaluate local 8-neighborhood (plus stay) deterministically.
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic ordering: prefer those that reduce chebyshev distance; then lexicographic.
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d0 = cheb(sx, sy, tx, ty)
        d1 = cheb(nx, ny, tx, ty)
        opp_d1 = cheb(ox, oy, tx, ty)
        # If we can still plausibly beat opponent for this target, prioritize reaching it.
        advantage = opp_d1 - d1
        # Also, if advantage is small, keep greedy: minimize our distance.
        score = (advantage, -(d1), -manh(nx, ny, tx, ty), -dx, -dy)
        scored.append((score, dx, dy))
    if not scored:
        return [0, 0]
    scored.sort(reverse=True)
    return [int(scored[0][1]), int(scored[0][2])]