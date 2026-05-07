def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy  # cheap proxy for progress on 8-neighbor

    # Pick resource: prioritize those I can reach significantly earlier than opponent
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None
    for (rx, ry) in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # strong preference for resources I can beat; mild preference toward center when contested
        beat = myd - opd
        center_bias = abs(rx - cx) + abs(ry - cy)
        key = (beat, myd, center_bias)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target_is_adj = abs(tx - sx) <= 1 and abs(ty - sy) <= 1
    best_move = (0, 0)
    best_score = None

    # Choose greedy move that avoids obstacles and minimizes distance to target
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        # If a resource is reachable in one step, prioritize it deterministically
        immediate = 0
        for (rx, ry) in res:
            if rx == nx and ry == ny:
                immediate = 1
                break
        # scoring: prefer immediate pickup, else approach target; add small tie-break away from opponent proximity
        dist = cheb(nx, ny, tx, ty)
        opp_close = cheb(nx, ny, ox, oy)
        score = (-immediate, dist, -opp_close if not target_is_adj else opp_close)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]