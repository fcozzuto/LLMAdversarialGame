def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role)
    movers = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x, y):
        dx = x - ox
        if dx < 0: dx = -dx
        dy = y - oy
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for ddx, ddy in movers:
            tx, ty = x + ddx, y + ddy
            if legal(tx, ty):
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if evader:
        target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        target = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    tx, ty = target
    best_dxdy = (0, 0)
    best_tuple = None

    for dx, dy in movers:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = cheb(nx, ny)
        mob = mobility(nx, ny)
        bias = -abs(nx - tx) - abs(ny - ty) if evader else abs(nx - tx) + abs(ny - ty)
        # Score tuple: (primary, secondary, tertiary) chosen deterministically by min/max via sign
        if evader:
            cand = (-dist, mob, bias)
            if best_tuple is None or cand > best_tuple:
                best_tuple, best_dxdy = cand, (dx, dy)
        else:
            cand = (dist, -mob, bias)
            if best_tuple is None or cand < best_tuple:
                best_tuple, best_dxdy = cand, (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]