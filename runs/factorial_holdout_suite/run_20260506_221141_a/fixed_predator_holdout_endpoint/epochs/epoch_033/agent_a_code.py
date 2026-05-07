def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cell_score(nx, ny):
        best = None
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer moves that reduce our distance relative to opponent, also break ties toward closer pickup.
            sc = (od - sd, -sd, -rx, -ry)
            if best is None or sc > best[0]:
                best = (sc, (rx, ry), sd)
        return best[0]

    best_move = None
    best_sc = None
    for dx, dy in sorted(legal, key=lambda t: (t[0], t[1])):
        nx, ny = sx + dx, sy + dy
        sc = cell_score(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]