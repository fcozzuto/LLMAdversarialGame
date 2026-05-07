def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except Exception:
            pass

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Pick resource: maximize opponent advantage (opponent farther), tie-break by self distance then position.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer winning: make do - ds large (opponent farther) and be closer ourselves.
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Greedy step toward target among legal moves (8-neighborhood + stay).
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds1 = man(nx, ny, tx, ty)
        do1 = man(ox, oy, tx, ty)
        # Primary: reduce our distance; Secondary: keep opponent not closer; Tertiary: deterministic tie.
        key = (-ds1, -(do1 - ds1), dx, dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]