def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = 3 if sx > (gw - 1) // 2 else (4 if sx < (gw - 1) // 2 else sx)
        ty = 3 if sy > (gh - 1) // 2 else (4 if sy < (gh - 1) // 2 else sy)
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -dist_cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_r = None
    best_val = -10**18
    for rx, ry in resources:
        d_me = dist_cheb(sx, sy, rx, ry)
        d_op = dist_cheb(ox, oy, rx, ry)
        # Prefer resources we are closer to; if tied, prefer closer and more "ahead" in lead.
        v = (d_op - d_me) * 10 - d_me
        if v > best_val:
            best_val = v
            best_r = (rx, ry)

    rx, ry = best_r
    # Desired step toward target (prefer diagonal when it helps).
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # Try the direct move first if legal; else choose best legal move toward this target with lead consideration.
    cand = [([dx, dy]), ([dx, 0]), ([0, dy]), ([0, 0]), ([-dx, dy]), ([dx, -dy])]
    for mv in cand:
        mdx, mdy = mv
        nx, ny = sx + mdx, sy + mdy
        if legal(nx, ny):
            return [mdx, mdy]

    best = [0, 0]
    bestv = -10**18
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue
        d_me = dist_cheb(nx, ny, rx, ry)
        d_op = dist_cheb(ox, oy, rx, ry)
        v = (d_op - d_me) * 10 - d_me
        if v > bestv:
            bestv = v
            best = [mdx, mdy]
    return best