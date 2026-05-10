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
    if ("purs" in sr and "evad" in sr):
        self_is_pursuer = True
    else:
        self_is_pursuer = ("purs" in sr) and ("evad" not in sr)
    if not ("purs" in sr or "evad" in sr) and ("purs" in orr):
        self_is_pursuer = False
    if ("evad" in sr) and ("purs" not in sr):
        self_is_pursuer = False

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return in_bounds(x, y) and (x, y) not in obs

    def dist(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            if safe(x + dx, y + dy):
                m += 1
        return m

    best = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        d = dist(nx, ny, ox, oy)
        mob = mobility(nx, ny)

        # Simple obstacle-aware "tangent" bias: prefer moves that don't immediately reduce mobility.
        # Pursuer tries to minimize distance; evader maximizes it.
        if self_is_pursuer:
            # Closer is better; also keep mobility.
            val = (-d, -mob, -nx, -ny)
        else:
            # Farther is better; also keep mobility.
            val = (d, mob, nx, ny)

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return best