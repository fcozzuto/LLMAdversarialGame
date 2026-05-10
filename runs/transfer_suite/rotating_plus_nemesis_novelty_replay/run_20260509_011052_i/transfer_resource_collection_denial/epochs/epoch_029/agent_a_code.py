def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        primary = ds - do  # prefer being closer (<=0)
        key = (primary > 0, primary, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), ds, do)
    tx, ty = best[1]

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                candidates.append((dx, dy, cheb(nx, ny, tx, ty)))

    if not candidates:
        return [0, 0]
    # tie-break: prefer moving that also increases distance from opponent (slightly)
    best_move = None
    for dx, dy, d_to in candidates:
        nx, ny = sx + dx, sy + dy
        d_opp = cheb(nx, ny, ox, oy)
        key = (d_to, -d_opp, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, (dx, dy))
    return [best_move[1][0], best_move[1][1]]