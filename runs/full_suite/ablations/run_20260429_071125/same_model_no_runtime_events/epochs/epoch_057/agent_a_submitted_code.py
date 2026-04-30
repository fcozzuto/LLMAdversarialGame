def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    sc = observation.get("scores") or [0, 0]
    s_self = sc[0] if len(sc) > 0 else 0
    s_opp = sc[1] if len(sc) > 1 else 0
    behind = s_self < s_opp

    best = None
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_opp = cheb(nx, ny, ox, oy)
        if resources:
            d_res = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            val = (-d_res * 1000) + (d_opp * 2)
        else:
            val = (d_opp * (-200 if behind else 200))
        if val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]