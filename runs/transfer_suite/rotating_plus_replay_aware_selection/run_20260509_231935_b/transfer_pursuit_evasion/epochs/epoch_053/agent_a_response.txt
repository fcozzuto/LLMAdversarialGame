def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("pursuit" in self_role and "evader" in opp_role) or ("evader" in opp_role and "pursuer" in self_role)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def center_bonus(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx, dy = x - cx, y - cy
        return -(dx * dx + dy * dy)

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        step_to_center = center_bonus(nx, ny)

        # Additional tie-breaker: avoid corners/crowding when evading, approach when pursuing.
        edge = (nx == 0) or (nx == w - 1) or (ny == 0) or (ny == h - 1)
        edge_pen = 25 if edge else 0

        # Count immediate escape/approach options (cheap local proxy)
        neigh = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        options = 0
        for ddx, ddy in neigh:
            tx, ty = nx + ddx, ny + ddy
            if legal(tx, ty):
                options += 1

        if is_evader:
            val = dist2 + 0.5 * options + 0.01 * step_to_center - edge_pen
            better = (best_val is None) or (val > best_val)
        else:
            val = -dist2 + 0.5 * options + 0.01 * step_to_center - edge_pen
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best_move = [dx, dy]

    return best_move