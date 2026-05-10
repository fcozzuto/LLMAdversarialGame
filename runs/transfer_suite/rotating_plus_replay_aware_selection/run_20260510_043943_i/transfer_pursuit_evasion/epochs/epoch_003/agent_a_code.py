def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("chaser" in self_role) or ("hunter" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    def obstacle_risk(nx, ny):
        # how "crowded" the neighborhood is by obstacles (prefer lower for evasion, higher for pursuit only if it helps)
        r = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    r += 1
        return r

    if is_pursuer:
        # Interception-lite: prefer capture, then minimize distance, and avoid "dead-ends" (high obstacle risk).
        best = None
        best_mv = (0, 0)
        for dx, dy, nx, ny in valid:
            cap = 1 if (nx == ox and ny == oy) else 0
            d = dist2(nx, ny, ox, oy)
            risk = obstacle_risk(nx, ny)
            key = (-cap, d, risk, dx, dy)
            if best is None or key < best:
                best = key
                best_mv = (dx, dy)
        return [best_mv[0], best_mv[1]]
    else:
        # Evasion: maximize distance; also try to move to opposite checkerboard color to reduce same-turn alignment.
        # Prefer moves with lower obstacle risk to avoid being funneled by zigzags.
        ocol = (ox + oy) & 1
        best = None
        best_mv = (0, 0)
        for dx, dy, nx, ny in valid:
            d = dist2(nx, ny, ox, oy)
            col_ok = 1 if (((nx + ny) & 1) != ocol) else 0
            risk = obstacle_risk(nx, ny)
            # avoid accidental capture
            cap_pen = 1 if (nx == ox and ny == oy) else 0
            key = (cap_pen, -d, -col_ok, risk, dx, dy)
            if best is None or key < best:
                best = key
                best_mv = (dx, dy)
        return [best_mv[0], best_mv[1]]