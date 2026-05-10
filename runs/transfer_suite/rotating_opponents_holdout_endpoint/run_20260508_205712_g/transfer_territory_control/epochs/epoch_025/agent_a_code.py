def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells", []) or []))
    resources = observation.get("resources", []) or []
    res = set((int(x), int(y)) for x, y in resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(x, y):
        if (x, y) in obs:
            return -10**9
        if (x, y) in self_terr:
            base = 3
        elif (x, y) in opp_terr:
            base = 8
        elif (x, y) in unclaimed:
            base = 10
        else:
            base = 0
        if (x, y) in res:
            base += 20
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        base -= int(abs(x - cx) + abs(y - cy))
        base += max(0, 10 - (abs(x - ox) + abs(y - oy)))
        if self_terr:
            adj = any(((x + dx, y + dy) in self_terr) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0))
            if adj:
                base += 6
        return base

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    bests = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        s = score_cell(nx, ny)
        if s > bests:
            bests = s
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best