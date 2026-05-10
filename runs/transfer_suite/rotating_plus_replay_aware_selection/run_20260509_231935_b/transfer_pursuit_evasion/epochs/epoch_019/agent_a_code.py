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

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def mobility(x, y):
        cnt = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                cnt += 1
        return cnt

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d_now = man(nx, ny, ox, oy)

        # Simple zigzag-aware "shadow": if evading, also consider cornering; if pursuing, aim to cut off.
        if self_is_pursuer:
            # Prefer smaller distance; penalize moves that reduce mobility.
            val = (-d_now, mobility(nx, ny))
        else:
            # Prefer larger distance; also prefer moving toward farthest corner deterministically.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy))
            corner_bias = -man(nx, ny, far_corner[0], far_corner[1])
            val = (d_now, corner_bias, mobility(nx, ny))

        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]