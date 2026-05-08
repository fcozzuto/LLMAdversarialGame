def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp = observation.get("opponent_position") or [None, None]
    ox, oy = opp[0], opp[1]
    ox = int(ox) if ox is not None else None
    oy = int(oy) if oy is not None else None

    def to_set(v):
        s = set()
        if not v:
            return s
        for p in v:
            if p is None or len(p) < 2:
                continue
            s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    opp_terr = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_sc = -10**18

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0
        if (nx, ny) in unclaimed:
            sc += 100
        if (nx, ny) in opp_terr:
            sc += 140
        if ox is not None and oy is not None and nx == ox and ny == oy:
            sc -= 2000
        # Prefer moving toward center while pushing for frontier capture
        sc += -0.5 * ((nx - cx) ** 2 + (ny - cy) ** 2) ** 0.5

        # Slightly prefer moves that reduce distance to opponent (aggressive)
        if ox is not None and oy is not None:
            sc += -1.0 * ((nx - ox) ** 2 + (ny - oy) ** 2) ** 0.5

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best