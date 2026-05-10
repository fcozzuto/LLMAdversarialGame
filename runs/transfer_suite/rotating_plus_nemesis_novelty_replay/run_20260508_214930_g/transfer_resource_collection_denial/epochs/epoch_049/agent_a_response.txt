def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target race: pick resource where we are closer than opponent, with small lead prioritized.
    best_t = None
    best_key = None
    for tx, ty in res:
        self_d = cheb(sx, sy, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Prefer: smaller (self_d - opp_d), then smaller self_d, then deterministic coord.
        key = (self_d - opp_d, self_d, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    dx = 0
    dy = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    # Candidate moves: greedy step toward target, then alternatives that avoid obstacles.
    candidates = []
    candidates.append((dx, dy))
    candidates.append((dx, 0))
    candidates.append((0, dy))
    if dx != 0 or dy != 0:
        candidates.append((-dx, dy))
        candidates.append((dx, -dy))
    candidates.append((0, 0))

    # Deterministic ordering tie-break: prefer moves that reduce chebyshev distance most.
    best = None
    best_score = None
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist = cheb(nx, ny, tx, ty)
        # Prefer smallest dist; then prefer moving in x, then y; then coord sign for determinism.
        score = (dist, -abs(mx), -abs(my), mx, my)
        if best_score is None or score < best_score:
            best_score = score
            best = (mx, my)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]