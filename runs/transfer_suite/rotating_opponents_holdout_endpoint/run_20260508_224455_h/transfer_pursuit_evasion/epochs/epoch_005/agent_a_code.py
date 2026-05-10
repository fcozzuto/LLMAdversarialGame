def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("evade" in role) or ("escape" in role)
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and not blocked(nx, ny):
                c += 1
        return c

    def edge_pen(x, y):
        # More penalty near walls for evader, less for pursuer
        d = min(x, y, w - 1 - x, h - 1 - y)
        return -d  # closer to edge => larger penalty magnitude

    best = None
    best_tuple = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        d = dist2(nx, ny)
        mob = mobility(nx, ny)
        ep = edge_pen(nx, ny)
        # Tie-break deterministically by preferring diagonals then stable lexicographic
        diag = 1 if dx != 0 and dy != 0 else 0
        # Score tuple: smaller is better for pursuer, larger for evader via sign flip
        if is_evader:
            tup = (-(d), -mob, -diag, ep, nx, ny)
        else:
            tup = (d, -mob, -diag, ep, nx, ny)

        if best_tuple is None or tup < best_tuple:
            best_tuple = tup
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]