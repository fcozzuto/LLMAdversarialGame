def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dsq(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx*dx + dy*dy

    cx0 = (w - 1) / 2.0; cy0 = (h - 1) / 2.0
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    best_target = None
    best_adv = None

    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        self_d = dsq(sx, sy, rx, ry)
        opp_d = dsq(ox, oy, rx, ry)
        adv = opp_d - self_d  # higher means we're closer
        center = abs(rx - cx0) + abs(ry - cy0)
        tie = (-adv, center, self_d)  # deterministic tie-break
        if best_target is None or tie < best_adv:
            best_adv = tie
            best_target = (rx, ry)

    rx, ry = best_target if best_target is not None else resources[0]

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd_self = dsq(nx, ny, rx, ry)
        nd_opp = dsq(ox, oy, rx, ry)
        adv = nd_opp - nd_self
        # Prefer moves that increase our advantage; penalize moving away and moving to edges.
        center_pen = abs(nx - cx0) + abs(ny - cy0)
        forward_pen = nd_self
        val = (-adv, forward_pen, center_pen, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move