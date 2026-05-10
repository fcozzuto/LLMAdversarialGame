def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("hunter" in self_role) or (self_role in ("pursuer", "pursuer_agent"))
    if not self_role and opponent_role:
        pursuer = not ("evad" in opponent_role)
    if not self_role and not opponent_role:
        pursuer = True

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy
        center2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        if pursuer:
            key = (dist2, center2, abs(dx) + abs(dy))
        else:
            key = (-dist2, -center2, abs(dx) + abs(dy))
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]