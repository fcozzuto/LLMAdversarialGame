def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []) or [])
    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)
    resources = observation.get("resources", []) or []
    res = set((p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(x1, y1, x2, y2): 
        return abs(x1 - x2) + abs(y1 - y2)

    # Deterministic tie-break: fixed order for direction scoring
    best = None; best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): 
            continue
        d_to_opp = manh(nx, ny, ox, oy)
        # Resource proximity
        d_to_res = min((manh(nx, ny, rx, ry) for (rx, ry) in res), default=9999)
        # Avoid moving into immediate capture zone when chasing; avoid being cornered when evading
        danger = -1000 if d_to_opp <= 1 else 0
        edge = -(1 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0)

        if pursuer:
            score = (-d_to_opp) + (5 if (nx, ny) in res else 0) - d_to_res * 0.1 + edge + danger
        else:
            score = (d_to_opp) + (3 if (nx, ny) in res else 0) - d_to_res * 0.05 + edge + danger

        if best is None or score > best_score:
            best_score = score; best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]