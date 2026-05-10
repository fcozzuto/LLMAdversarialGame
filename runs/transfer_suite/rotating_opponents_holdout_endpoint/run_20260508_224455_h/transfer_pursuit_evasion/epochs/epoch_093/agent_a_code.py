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
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    def blocked(nx, ny):
        return not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) and ("pursuer" not in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    corner = (0, 0)
    if (ox > (w - 1) // 2) and (oy > (h - 1) // 2):
        corner = (0, h - 1)
    elif (ox <= (w - 1) // 2) and (oy > (h - 1) // 2):
        corner = (w - 1, 0)
    elif (ox > (w - 1) // 2) and (oy <= (h - 1) // 2):
        corner = (0, 0)
    else:
        corner = (w - 1, h - 1)

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        center_pen = ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.0007
        if evader:
            target_x, target_y = corner
            t2 = (nx - target_x) * (nx - target_x) + (ny - target_y) * (ny - target_y)
            val = (-d2) + (-t2) * 0.01 + center_pen
        else:
            val = d2 + center_pen
        if best is None or val < best:
            best = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]