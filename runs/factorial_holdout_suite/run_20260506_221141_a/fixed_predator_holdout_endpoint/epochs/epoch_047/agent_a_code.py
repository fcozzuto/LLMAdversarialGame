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
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # diagonal-allowed

    valids = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                valids.append((x, y))
    if not valids:
        return [0, 0]

    best_res = None
    best_sc = -10**18
    for rx, ry in valids:
        self_d = dist((sx, sy), (rx, ry))
        opp_d = dist((ox, oy), (rx, ry))
        # Big preference for resources we can reach no later; otherwise fight only if we reduce opponent lead.
        if self_d <= opp_d:
            sc = 1_000_000 + (opp_d - self_d) * 50 - self_d * 2
        else:
            sc = (opp_d - self_d) * 30 - self_d * 1
        if sc > best_sc:
            best_sc = sc
            best_res = (rx, ry)

    tx, ty = best_res
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = (0, 0)
    best_msc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = dist((nx, ny), (tx, ty))
        # Prefer moves that improve our race and slightly worsen opponent path to the same target.
        opp_d = dist((ox, oy), (tx, ty))
        msc = -myd * 10 + (opp_d - myd) * 2
        # Add micro-denial: if opponent is adjacent to target, avoid drifting away.
        if opp_d == 1:
            msc += 5 - myd
        if msc > best_msc:
            best_msc = msc
            best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]