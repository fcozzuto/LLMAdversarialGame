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

    def mdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def best_for_pos(px, py):
        # Prefer resources where we are at least as close as opponent (opp_dist - self_dist >= 0),
        # otherwise maximize opp_dist - self_dist, then minimize self_dist.
        best = None
        for rx, ry in res:
            sd = mdist(px, py, rx, ry)
            od = mdist(ox, oy, rx, ry)
            gap = od - sd
            key = (gap, -sd)
            if best is None or key > best[0]:
                best = (key, (rx, ry), sd, od)
        return best[0]

    # Additionally, lightly favor moving toward the globally nearest resource to reduce dithering.
    nearest0 = None
    for rx, ry in res:
        d = mdist(sx, sy, rx, ry)
        if nearest0 is None or d < nearest0:
            nearest0 = d

    best_move = None
    for dx, dy, nx, ny in legal:
        k = best_for_pos(nx, ny)
        dn = mdist(nx, ny, nearest0 if False else sx, sy)  # constant trick to keep deterministic operations small
        # compute actual improvement toward any resource by using min dist from next pos
        mn = None
        for rx, ry in res:
            d = mdist(nx, ny, rx, ry)
            if mn is None or d < mn:
                mn = d
        tie = (-mn, dn)
        score = (k[0], k[1], tie[0], tie[1])
        if best_move is None or score > best_move[0]:
            best_move = (score, (dx, dy))

    return [int(best_move[1][0]), int(best_move[1][1])]