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
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def adj_block_cnt(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                c += 1
        return c

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) == (sx, sy):
            pass
        if not free(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        block_cnt = adj_block_cnt(nx, ny)
        # Secondary preference: maximize local mobility
        mobility = 0
        for ddx, ddy in dirs[:4]:  # cheap: cardinal-ish
            tx, ty = nx + ddx, ny + ddy
            if free(tx, ty):
                mobility += 1

        if am_evader:
            # flee + avoid crowded/dead ends
            key = (d, -block_cnt, mobility, -abs(nx - (w - 1 - ox)) - abs(ny - (h - 1 - oy)))
        else:
            # pursue + reduce blocking risk
            key = (-d, block_cnt, -mobility, abs(nx - ox) + abs(ny - oy))

        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]