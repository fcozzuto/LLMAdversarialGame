def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("purs" in sr) and ("evad" not in sr)
    if not ("purs" in sr or "evad" in sr) and ("purs" in orr):
        self_is_pursuer = False
    if ("evad" in sr) and ("purs" not in sr):
        self_is_pursuer = False
    if ("purs" in sr) and ("evad" in sr):
        self_is_pursuer = True

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return in_bounds(x, y) and (x, y) not in obs

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                c += 1
        return c

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        mob = mobility(nx, ny)
        # Deterministic scoring: capture race + obstacle-aware mobility bias.
        if self_is_pursuer:
            val = dist2 - 0.15 * mob
            if best_val is None or val < best_val:
                best_val, best = val, [dx, dy]
        else:
            # For evader: also drift away from the nearest corner that the pursuer can line up on.
            corner = (0, 0)
            # Prefer corner farthest from pursuer
            corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
            farc = corners[0]
            far_d = -1
            for cx, cy in corners:
                d = (cx - ox) * (cx - ox) + (cy - oy) * (cy - oy)
                if d > far_d:
                    far_d, farc = d, (cx, cy)
            cx, cy = farc
            drift = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            val = -dist2 + 0.08 * mob - 0.02 * drift
            if best_val is None or val < best_val:
                best_val, best = val, [dx, dy]

    if best is None:
        return [0, 0]
    return best