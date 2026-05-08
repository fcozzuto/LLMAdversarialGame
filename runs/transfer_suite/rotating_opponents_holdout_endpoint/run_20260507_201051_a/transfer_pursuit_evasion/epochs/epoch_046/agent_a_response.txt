def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy
    def block_score(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                c += 1
        return c  # lower is better (more freedom)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            d = dist2(nx, ny)
            b = block_score(nx, ny)
            candidates.append((nx, ny, dx, dy, d, b))

    if not candidates:
        return [0, 0]

    best = None
    if am_evader:
        # maximize distance; prefer fewer blocks (more mobility)
        for _, _, dx, dy, d, b in candidates:
            key = (d, -b, -abs((sx + dx) - (w - 1) / 2.0), -abs((sy + dy) - (h - 1) / 2.0))
            if best is None or key > best[0]:
                best = (key, dx, dy)
    else:
        # minimize distance; prefer fewer blocks (avoid wall traps)
        for _, _, dx, dy, d, b in candidates:
            key = (-d, -b, abs((sx + dx) - (w - 1) / 2.0) + abs((sy + dy) - (h - 1) / 2.0))
            if best is None or key > best[0]:
                best = (key, dx, dy)

    return [int(best[1]), int(best[2])]