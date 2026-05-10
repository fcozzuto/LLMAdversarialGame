def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    oppt = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opppos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = opppos[0], opppos[1]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score_cell(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        gain = 0.0
        if (nx, ny) in un:
            gain += 2.2
        if (nx, ny) in oppt:
            gain += 3.0
        if (nx, ny) in selft:
            gain -= 0.2

        # Expansion: prefer moving toward unclaimed and away from opponent core
        if un:
            # distance to nearest unclaimed (deterministic, but capped by few samples)
            ux_list = list(un)
            step = max(1, len(ux_list) // 20)
            dmin = 10**9
            for i in range(0, len(ux_list), step):
                ux, uy = ux_list[i]
                d = abs(ux - nx) + abs(uy - ny)
                if d < dmin:
                    dmin = d
            gain += 0.35 * (16 - dmin)
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        gain += 0.05 * d_to_opp

        # Border pressure: number of adjacent unclaimed/opponent cells
        adj = 0
        adj_opp = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            ax, ay = nx + dx, ny + dy
            if not inb(ax, ay):
                continue
            if (ax, ay) in un:
                adj += 1
            if (ax, ay) in oppt:
                adj_opp += 1
        gain += 0.25 * adj + 0.45 * adj_opp

        # Avoid getting wedged: prefer staying with at least one free neighbor (soft)
        free_nei = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            ax, ay = nx + dx, ny + dy
            if inb(ax, ay) and (ax, ay) not in obs:
                free_nei += 1
        gain += 0.1 * free_nei
        return gain

    best = (score_cell(sx, sy), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        val = score_cell(nx, ny)
        if val > best[0] or (val == best[0] and (dx, dy) < (best[1], best[2])):
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]