def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in srole) or ("catch" in srole) or ("seeker" in srole) or ("chase" in srole)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    def center_bias(x, y):
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        # Favor center: larger is better.
        return -((abs(x - cx) + abs(y - cy)))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = (None, None, -10**9)
    if is_pursuer:
        # Greedy chase: minimize distance to opponent; avoid obstacles.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in oset:
                continue
            d = cheb(nx, ny)
            # Tie-break: prefer moves that increase progress along x then y (deterministic).
            t = (-d, -(abs(nx - ox) < abs(sx - ox) or abs(ny - oy) < abs(sy - oy)), -(abs(nx - ox)), -(abs(ny - oy)))
            # Convert tuple to scalar deterministically.
            val = -d * 1000000 + (-abs(nx - ox)) * 1000 + (-abs(ny - oy))
            if best[2] < val:
                best = (dx, dy, val)
    else:
        # Evade: maximize distance, but bias toward center to avoid getting pinned by cornering.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in oset:
                continue
            d = cheb(nx, ny)
            # Additional safety: discourage stepping adjacent to obstacles (not perfect, but cheap).
            adj = 0
            for oxp, oyp in oset:
                if max(abs(nx - oxp), abs(ny - oyp)) <= 1:
                    adj += 1
                    if adj >= 2:
                        break
            val = d * 1000000 + center_bias(nx, ny) * 1000 - adj * 500
            if best[2] < val:
                best = (dx, dy, val)

    if best[0] is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]