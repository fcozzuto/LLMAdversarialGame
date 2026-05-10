def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inside(x, y) and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort(key=lambda d: (d[0], d[1]))  # deterministic tie-break

    r = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in r) or ("chaser" in r) or ("hunter" in r)

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if legal(nx, ny):
                c += 1
        return c

    def obstacle_near(x, y):
        c = 0
        for (ox2, oy2) in obs:
            if abs(ox2 - x) <= 1 and abs(oy2 - y) <= 1:
                c += 1
        return c

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        near = obstacle_near(nx, ny)

        if is_pursuer:
            val = (-d, -mob, near, dx, dy)  # want smallest distance
        else:
            val = (-(-d), mob, near, dx, dy)  # want largest distance

        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]