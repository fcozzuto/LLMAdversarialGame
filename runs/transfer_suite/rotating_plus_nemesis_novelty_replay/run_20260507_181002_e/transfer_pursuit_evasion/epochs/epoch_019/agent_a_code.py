def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    srole = str(observation.get("self_role", "")).lower()
    orole = str(observation.get("opponent_role", "")).lower()
    i_am_pursuer = (("pursuer" in srole) or ("chaser" in srole) or ("catch" in srole) or ("pursuit" in srole))
    if "evader" in srole or "evad" in srole:
        i_am_pursuer = False
    if (("pursuer" in orole) or ("chaser" in orole) or ("catch" in orole) or ("pursuit" in orole)):
        i_am_pursuer = False

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for ddx, ddy in dirs:
            if free(x + ddx, y + ddy):
                c += 1
        return c

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = dist2(nx, ny)
        mob = mobility(nx, ny)
        direct = (abs(nx - ox) + abs(ny - oy))  # L1 to break ties consistently

        # Materially different from balanced: pure greedy distance with obstacle-aware safety.
        # Pursuer: minimize distance, avoid low-mobility positions.
        # Evader: maximize distance, also prefer escapes with higher mobility.
        if i_am_pursuer:
            val = d * 1000 - mob * 5 + direct
        else:
            val = -d * 1000 - mob * 2 + direct  # more negative is better

        if best is None or val < best_val or (val == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = val

    return [int(best[0]), int(best[1])]