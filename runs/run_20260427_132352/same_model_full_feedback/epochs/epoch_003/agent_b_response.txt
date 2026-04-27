def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best, bestv = (0, 0), -10**18
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            v = md(nx, ny, ox, oy) * 1.2 + md(nx, ny, cx, cy) * 0.05
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Choose our best target by advantage (opponent farther than us).
    best_ours, best_key = None, None
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        key = (do - ds, -ds, -do)  # maximize advantage, then closer to us, then farther from opponent
        if best_key is None or key > best_key:
            best_key, best_ours = key, (rx, ry)
    tx, ty = best_ours

    # Opponent likely target: nearest resource to opponent.
    opp_target = None
    opp_bd = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = md(ox, oy, rx, ry)
        if opp_bd is None or d < opp_bd or (d == opp_bd and md(sx, sy, rx, ry) > md(sx, sy, opp_target[0], opp_target[1]) if opp_target else False):
            opp_bd, opp_target = d, (rx, ry)
    px, py = opp_target if opp_target else (tx, ty)

    best, bestv = (0, 0), -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = md(nx, ny, tx, ty)
        do = md(ox, oy, tx, ty)
        adv = do - ds

        d_to_opp = md(nx, ny, px, py)
        v = adv * 10.0 - d_to_opp * 3.0  # contest opponent's likely target
        v += md(nx, ny, ox, oy) * 0.05  # slight safety
        if (nx, ny) == (px, py):
            v += 100.0
        if (nx, ny) == (tx, ty):
            v += 30.0

        if v > bestv:
            bestv, best = v, (dx, dy)

    return [best[0], best[1]]