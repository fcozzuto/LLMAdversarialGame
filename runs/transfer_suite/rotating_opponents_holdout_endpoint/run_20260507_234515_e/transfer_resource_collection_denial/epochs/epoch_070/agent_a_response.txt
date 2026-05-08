def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Pick a resource: prioritize ones we reach first; then shorter path; then deterministic ordering.
    best = None
    best_key = None
    for rx, ry in res:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        key = (dS - dO, dS, rx, ry)  # smaller is better
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Choose a valid one-step move that reduces distance to target; tie-break deterministically.
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            deltas.append((dx, dy))
    deltas.sort(key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1]))  # deterministic

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        # Prefer immediate capture if stepping onto resource.
        on_res = 1 if (nx, ny) == (tx, ty) else 0
        score = (0 if on_res else 1, dist, abs(dx) + abs(dy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]