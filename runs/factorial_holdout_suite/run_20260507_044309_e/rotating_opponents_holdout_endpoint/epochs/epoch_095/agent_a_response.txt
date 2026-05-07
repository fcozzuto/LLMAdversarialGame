def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy  # 8-neighbor proxy

    # Pick target we can reach earlier than opponent; break ties by larger slack and then nearer.
    best = None
    best_key = None
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        slack = opd - myd
        # Higher slack is better; then smaller myd; then deterministic by coordinates.
        key = (slack, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Candidate moves: 8 directions + stay (dx,dy in {-1,0,1}).
    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Greedy toward target with one-step opponent pressure check.
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_next = cheb(nx, ny, tx, ty)
        opp_next = cheb(ox, oy, tx, ty)
        # Prefer moves that reduce our distance; if equal, prefer increasing our advantage.
        key = (-my_next, (opp_next - my_next), -abs(nx - ox) - abs(ny - oy))
        cand.append((key, dx, dy))
    if not cand:
        return [0, 0]

    cand.sort(reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]