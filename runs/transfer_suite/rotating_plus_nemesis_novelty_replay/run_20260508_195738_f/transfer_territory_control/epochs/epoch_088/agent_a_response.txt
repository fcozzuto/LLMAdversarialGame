def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    oppt = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def adj_exists(x, y, s):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in s:
                    return True
        return False

    # Threat: our cells adjacent to opponent territory (counterclaim pressure)
    threat = adj_exists(sx, sy, oppt)

    # Precompute nearest opponent-territory distance from any candidate (for deterministic threat inversion)
    opp_list = list(oppt)
    def nearest_opp_dist(x, y):
        if not opp_list:
            return 10**9
        best = 10**9
        for px, py in opp_list:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    best_mv = [0, 0]
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0
        sc = 0
        if (nx, ny) in oppt:
            sc += 10  # immediate flip of opponent-controlled cell
        elif (nx, ny) in un:
            sc += 4   # claim unclaimed
        elif (nx, ny) in selft:
            sc += 1   # consolidate
        else:
            sc += 0

        # Attack preference: move closer to opponent territory when we can take cells
        d_opp = nearest_opp_dist(nx, ny)
        sc += (6 - min(d_opp, 6))  # up to +6

        # Defense: if currently on/near a threatened border, avoid drifting away
        d_opponent_pos = abs(nx - ox) + abs(ny - oy)
        base_d = abs(sx - ox) + abs(sy - oy)
        if threat:
            sc += (base_d - d_opponent_pos) * 0.5  # stay closer to deter counterclaims
        else:
            sc += (base_d - d_opponent_pos) * 0.2  # slight centralization toward opponent frontier

        # Border cohesion: prefer cells adjacent to our territory (avoid lonely grabs)
        sc += 2 if adj_exists(nx, ny, selft) else 0

        # Deterministic tie-break: fixed dir ordering already; maximize then keep earlier
        if sc > best_sc:
            best_sc = sc
            best_mv = [dx, dy]
    return best_mv