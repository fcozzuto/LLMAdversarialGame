def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Heuristic: claim unclaimed toward the center; pressure opponent if adjacent/near.
    opp_list = list(opp)
    def nearest_opp_dist(nx, ny):
        if not opp_list:
            return 10**9
        dmin = 10**9
        for px, py in opp_list:
            d = abs(px - nx) + abs(py - ny)
            if d < dmin:
                dmin = d
        return dmin

    def opp_adj(nx, ny):
        return any((nx + dx, ny + dy) in opp for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy))

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = 0.0
        if (nx, ny) in unclaimed:
            v += 2.3
        elif (nx, ny) in opp:
            v += 2.0
        elif (nx, ny) in selft:
            v += 0.4
        else:
            v += 0.8  # unknown/edge
        # Pull toward center
        dc = abs(nx - cx) + abs(ny - cy)
        v += 3.0 / (1.0 + dc)
        # Pressure opponent
        do = nearest_opp_dist(nx, ny)
        v += 2.2 / (1.0 + do)
        if opp_adj(nx, ny):
            v += 1.2
        # Slightly discourage oscillation: prefer non-stay unless clearly best
        if dx == 0 and dy == 0:
            v -= 0.15
        if best is None or v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]