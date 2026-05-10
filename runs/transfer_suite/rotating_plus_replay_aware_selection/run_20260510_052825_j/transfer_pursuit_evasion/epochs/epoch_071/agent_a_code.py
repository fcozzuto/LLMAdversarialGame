def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def deg(x, y):
        c = 0
        for dx, dy in moves:
            if inb(x + dx, y + dy):
                c += 1
        return c

    role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in role) or ("pursuer" in role)

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        safety = deg(nx, ny)
        edge = 1 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0
        if is_pursuer:
            score = (-dist, -safety, -edge, dx, dy)  # minimize dist, avoid cramped, avoid edges
        else:
            score = (dist, safety, edge, -dx, -dy)  # maximize dist, prefer mobility
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move