def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target: maximize opponent advantage margin; tie-break by our closeness.
    best = None
    best_key = (-10**9, 10**9)
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        margin = d_opp - d_self  # larger means we are closer
        key = (margin, d_self)
        if key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Prefer moves that reduce our distance to target; if tied, improve opponent distance (deny).
    bestm = (0, 0)
    bestk = (10**9, -10**9, 0)  # (our_dist, -opp_dist, stable tie)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Prefer staying if already on target-ish and no better move exists (handled by distance).
        tie = 0
        if dx == 0 and dy == 0:
            tie = 1
        k = (d_self, -d_opp, tie)
        if k < bestk:
            bestk = k
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]