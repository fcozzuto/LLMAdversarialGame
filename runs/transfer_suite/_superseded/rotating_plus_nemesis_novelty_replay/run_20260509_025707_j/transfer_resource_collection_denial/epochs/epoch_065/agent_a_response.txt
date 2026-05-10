def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Distance with diagonal moves allowed: Chebyshev
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res_set = set()
    for r in resources:
        if r is not None and len(r) >= 2:
            res_set.add((r[0], r[1]))

    if (sx, sy) in res_set:
        return [0, 0]

    if not resources:
        return [0, 0]

    best = None  # (score_tuple, [dx,dy])
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate this move by best target according to advantage vs opponent.
        move_best = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue

            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            adv = opd - myd
            # Prefer winning targets (positive adv), then higher adv, then smaller myd, then larger opd.
            # Also small tie-break toward targets not adjacent to opponent to reduce interference.
            opp_adj = 1 if dist(ox, oy, rx, ry) <= 1 else 0
            cand = (adv, -myd, opd, -opp_adj)
            if move_best is None or cand > move_best:
                move_best = cand

        if move_best is None:
            continue

        # If no winning target exists, still prefer best move against opponent: maximize cand[0], then cand[1].
        if best is None or move_best > best[0]:
            best = (move_best, [dx, dy])

    return best[1] if best is not None else [0, 0]