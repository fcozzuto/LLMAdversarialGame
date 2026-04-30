def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    my = (sx, sy)
    opp = (ox, oy)

    if resources:
        best_t = None
        best_key = None
        for t in resources:
            myd = cheb(my, t)
            opd = cheb(opp, t)
            key = (myd - opd, myd, t[0], t[1])
            if best_key is None or key < best_key:
                best_key = key
                best_t = t
        tx, ty = best_t
    else:
        tx, ty = ox, oy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = int(observation.get("turn_index") or 0)
    r = (ti * 3) % 9
    moves = moves[r:] + moves[:r]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nmy = (nx, ny)
        d = cheb(nmy, (tx, ty))
        dod = cheb(nmy, opp)
        opp_d = cheb(opp, (tx, ty))
        # Higher is better
        val = (-10 * d) + (2 * dod) + (4 * (opp_d - cheb(nmy, (tx, ty))))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]