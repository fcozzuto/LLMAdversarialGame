def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = w // 2, h // 2
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive => we are earlier
        center_bias = cheb(rx, ry, cx, cy)
        # Favor earlier capture; if not, prefer far from opponent; deterministic tie-breaks
        key = (-adv, -do, ds, center_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key, best = key, (rx, ry)

    if best is None:
        # Drift to center, but keep deterministic obstacle-safe stepping
        tx, ty = cx, cy
    else:
        tx, ty = best

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    opp_next_influence = 0.0
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Greedy: get closer to target; if tied, prefer increasing our lead over opponent.
        # Also add slight preference to move away from opponent if resources are scarce/tied.
        escape = cheb(nx, ny, ox, oy)
        key = (self_d, opp_d - self_d, -escape, dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key, best_m = key, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]