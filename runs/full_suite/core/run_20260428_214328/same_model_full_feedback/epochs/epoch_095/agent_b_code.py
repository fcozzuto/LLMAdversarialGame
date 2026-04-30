def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = sorted(dirs)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Prefer center, but keep some distance from opponent
            val = (cheb(nx, ny, tx, ty), -cheb(nx, ny, ox, oy), dx, dy)
            if best is None or val < best:
                best = val
        if best is None:
            return [0, 0]
        return [best[2], best[3]]

    # Pick target where we have deterministic "advantage" over opponent in chebyshev distance
    opp_bestd = None
    target = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # positive means we are closer or equal
        key = (-(adv), sd, rx, ry)
        if target is None or key < target:
            target = key
            opp_bestd = (adv, sd, od, rx, ry)
    rx, ry = opp_bestd[3], opp_bestd[4]

    # Greedy move toward chosen target, with tie-breakers favoring survival/denial vs opponent
    best_move = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to = cheb(nx, ny, rx, ry)
        d_opp = cheb(nx, ny, ox, oy)
        # Primary: get closer to target. Secondary: keep farther from opponent.
        val = (d_to, -d_opp, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]