def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("pursuer" in self_role) or ("pursuer" in opp_role) and ("evader" in self_role) == False
    # if roles unclear, assume pursuit_evasion default: self_role indicates pursuer
    if ("pursuer" not in self_role) and ("evader" not in self_role) and ("pursuer" in opp_role):
        self_is_pursuer = False

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Deterministic ordering for tie-breaking: nearer toward opponent direction first
    tx = 0 if ox == sx else (1 if ox > sx else -1)
    ty = 0 if oy == sy else (1 if oy > sy else -1)
    pref = []
    for dx, dy in moves:
        pref.append((-(dx == tx) - (dy == ty), dx, dy))
    pref.sort()
    moves = [(dx, dy) for _, dx, dy in pref]

    best = None
    best_val = None
    # Aim: pursuer minimizes distance; evader maximizes distance.
    # Add obstacle "shadow": penalize moving adjacent to obstacles (likely wall-running trap).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny)
        # adjacency penalty to avoid getting boxed against walls by runner
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in blocked:
                    adj += 1
        # slight bias to approach escape line (center) to avoid being cornered
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = abs(nx - cx) + abs(ny - cy)
        # score
        if self_is_pursuer:
            val = d * 1000 + adj * 50 + center * 3
        else:
            val = (-d) * 1000 + adj * 30 - center * 2
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]