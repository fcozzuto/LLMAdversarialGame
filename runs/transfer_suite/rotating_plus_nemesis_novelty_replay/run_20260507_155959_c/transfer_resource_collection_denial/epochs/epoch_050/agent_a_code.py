def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = observation.get("turns_remaining", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if (sx, sy) in obs:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    # Opponent likely target: closest remaining resource to them.
    opp_best = None; opp_best_d = 10**9
    for rx, ry in res:
        d = md(ox, oy, rx, ry)
        if d < opp_best_d:
            opp_best_d = d
            opp_best = (rx, ry)

    # Decide our target: prefer stealing (opp_dist - self_dist), but if we can't steal
    # opponent's likely target, deny by moving toward the next-best "stealable" resource.
    best_t = None; best_key = None
    for rx, ry in res:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        steal_gap = do - ds
        # Slightly favor nearer resources late-game
        late_bias = -ds * (0.5 + (turns_remaining / 100.0))
        # If this is the opponent's best target, increase pressure to deny it
        deny_boost = 3.0 if (rx, ry) == opp_best else 0.0
        key = (steal_gap + deny_boost, late_bias, -ds)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # One-step obstacle-aware move toward target. Deterministic order.
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_m = (0, 0); best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_to_t = md(nx, ny, tx, ty)
        # If we're already on target, stay.
        score = (d_to_t, md(nx, ny, ox, oy))
        if best_score is None or score < best_score:
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]