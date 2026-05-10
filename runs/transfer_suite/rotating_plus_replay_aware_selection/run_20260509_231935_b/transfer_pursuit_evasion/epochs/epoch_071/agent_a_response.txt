def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("evader" not in self_role and "pursuer" not in opp_role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    if i_am_pursuer:
        # Greedy chase: minimize squared distance to opponent; slight preference to keep moving
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            move_pen = 0 if (dx == 0 and dy == 0) else -0.001
            val = dist2 + move_pen
            if best is None or val < best_val:
                best = (dx, dy)
                best_val = val
    else:
        # Evasive: maximize squared distance to pursuer; tie-break toward borders to limit pursuer options
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            edge = min(nx, w - 1 - nx, ny, h - 1 - ny)
            # Prefer larger edge distance from center (i.e., nearer to edges) deterministically
            edge_pref = (3.5 - edge) * 0.0005
            val = dist2 + edge_pref
            if best is None or val > best_val:
                best = (dx, dy)
                best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]