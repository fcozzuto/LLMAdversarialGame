def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    self_ter = set(map(tuple, observation.get("self_territory", []) or []))
    opp_ter = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))

    resources = observation.get("resources", []) or []
    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_cells.append((int(r[0]), int(r[1])))

    center = (w - 1) / 2.0, (h - 1) / 2.0
    opp_cnt = int(observation.get("opponent_territory_count", len(opp_ter)) or 0)
    my_cnt = int(observation.get("self_territory_count", len(self_ter)) or 0)

    def adj_to_self(nx, ny):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (nx + ddx, ny + ddy) in self_ter:
                    return 1
        return 0

    def step_score(nx, ny):
        if (nx, ny) in obstacles or not inb(nx, ny):
            return -10**9
        base = 0.0
        if (nx, ny) in self_ter:
            base = 1.0
        elif (nx, ny) in opp_ter:
            base = 20.0 if opp_cnt >= my_cnt else 15.0
        elif (nx, ny) in unclaimed:
            base = 8.0
        else:
            base = 3.0

        # expansion vs offense
        dist_center = abs(nx - center[0]) + abs(ny - center[1])
        base += -0.25 * dist_center

        if res_cells:
            rx, ry = min(res_cells, key=lambda p: abs(p[0] - nx) + abs(p[1] - ny))
            base += -0.35 * (abs(rx - nx) + abs(ry - ny))

        base += 1.2 * adj_to_self(nx, ny)

        # prefer moving toward opponent if we can flip immediately / close in
        if opp_ter:
            d_opp = min(abs(p[0] - nx) + abs(p[1] - ny) for p in opp_ter)
            base += (1.8 / (1 + d_opp)) if (nx, ny) in opp_ter else (0.9 / (1 + d_opp))

        # keep moving mostly; discourage staying unless it is best
        base += -0.05 * (0 if (nx == sx and ny == sy) else 1)

        return base

    best = None
    best_sc = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            sc = step_score(nx, ny)
            if sc > best_sc:
                best_sc = sc
                best = (dx, dy)

    return [int(best[0]), int(best[1])]