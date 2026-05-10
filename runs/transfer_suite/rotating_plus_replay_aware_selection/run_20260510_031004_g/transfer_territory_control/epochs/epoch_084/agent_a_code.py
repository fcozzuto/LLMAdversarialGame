def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    neigh = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    best = None
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        v = 0
        if (nx, ny) in self_terr:
            v += 1
        if (nx, ny) in unclaimed:
            v += 6
        if (nx, ny) in opp_terr:
            v -= 3  # generally avoid walking into opponent territory unless it opens space

        adj_unclaimed = 0
        adj_empty = 0
        adj_opp = 0
        for ox, oy in neigh:
            tx, ty = nx + ox, ny + oy
            if not inb(tx, ty) or blocked(tx, ty):
                continue
            if (tx, ty) in unclaimed:
                adj_unclaimed += 1
            elif (tx, ty) not in self_terr and (tx, ty) not in opp_terr:
                adj_empty += 1
            if (tx, ty) in opp_terr:
                adj_opp += 1

        v += adj_unclaimed * 5
        v += adj_empty * 1
        v -= adj_opp * 0.5
        # slight bias to expand toward center to reduce being edge-trapped
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        v -= (abs(nx - cx) + abs(ny - cy)) * 0.02

        if v > bestv:
            bestv = v
            best = [dx, dy]
        elif v == bestv:
            if best is None or (dx, dy) < tuple(best):
                best = [dx, dy]

    return best