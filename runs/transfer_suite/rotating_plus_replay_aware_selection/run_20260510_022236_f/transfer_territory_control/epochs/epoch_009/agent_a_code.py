def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obs = to_set(observation.get("obstacles"))
    un = to_set(observation.get("unclaimed_cells", observation.get("unclaimed")))
    res = to_set(observation.get("resources"))
    st = to_set(observation.get("self_territory"))
    ot = to_set(observation.get("opponent_territory"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj(x, y, S):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in S:
                        return True
        return False

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_value(x, y):
        if (x, y) in obs:
            return -10**9
        v = 0
        if (x, y) in res:
            v += 60
        if (x, y) in un:
            v += 35
        if (x, y) in ot:
            v += 28  # flipping on entry
        if (x, y) in st:
            v += 6
        # Prefer pushing toward opponent side while keeping away from obstacles.
        v += 3 * (w - 1 - man(x, y, ox, oy)) // (w if w else 1)
        if adj(x, y, obs):
            v -= 10
        # If close to opponent territory, take/maintain contact.
        if adj(x, y, ot):
            v += 12
        return v

    # Choose best immediate move; tie-break deterministically by dx, then dy.
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        v = cell_value(nx, ny)
        # Small preference for not stepping away from the nearest unclaimed cell.
        if un:
            ux, uy = min(un, key=lambda p: (man(nx, ny, p[0], p[1]), p[0], p[1]))
            v += 2 * (-man(nx, ny, ux, uy))
        if (v, dx, dy) > best:
            best = (v, dx, dy)
    return [int(best[1]), int(best[2])]