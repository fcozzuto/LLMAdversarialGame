def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = [(x, y) for (x, y) in resources if (x, y) not in obstacles]
    if not res:
        best = max(legal, key=lambda t: cheb(t[2], t[3], ox, oy))
        return [best[0], best[1]]

    best_dxdy = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        my_d_to = []
        for rx, ry in res:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            my_d_to.append((md, od, rx, ry))
        # Primary: win/contest a resource (prefer where we are closer than opponent).
        # Score is max over resources; also add slight bias to overall closeness.
        best_r_score = -10**18
        for md, od, rx, ry in my_d_to:
            # contested advantage: positive if we are at least as close as opponent
            adv = od - md
            # if we are closer, strongly prefer; otherwise still prefer to reduce their lead
            closeness = 16 - md  # within grid, md <= 7/8-ish
            block_bias = 0
            # tiny penalty for stepping near opponent when advantage is weak
            op_close = cheb(nx, ny, ox, oy)
            if adv < 0:
                block_bias -= (6 - op_close if op_close < 6 else 0)
            s = adv * 10 + closeness * (3 if adv >= 0 else 1) + block_bias
            if s > best_r_score:
                best_r_score = s
        # Secondary: if contest scores tie, prefer moving away from opponent when no contested advantage exists.
        op_next = cheb(nx, ny, ox, oy)
        my_next_self = 0  # not used; keep deterministic tie-breaker with resource distances
        tie = best_r_score * 1000 + (op_next if best_r_score < 0 else -op_next) - md  # md from last loop is overwritten; fix:
        # recompute md for deterministic tie-break
        md_min = min(m for m, _, _, _ in my_d_to)
        tie = best_r_score * 1000 + (op_next if best_r_score < 0 else -op_next) - md_min
        if tie > best_score:
            best_score = tie
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]