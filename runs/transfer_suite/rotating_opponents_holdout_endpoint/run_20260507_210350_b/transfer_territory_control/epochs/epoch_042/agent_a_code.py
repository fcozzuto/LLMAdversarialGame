def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    self_terr = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []))
    opp_terr = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []))
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []))

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adj_our(nx, ny):
        for dx, dy in neigh4:
            if (nx + dx, ny + dy) in self_terr:
                return 1
        return 0

    my_cnt = int(observation.get("self_territory_count", len(self_terr)) or len(self_terr))
    opp_cnt = int(observation.get("opponent_territory_count", len(opp_terr)) or len(opp_terr))

    best = [0, 0]
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist_center = abs(nx - cx) + abs(ny - cy)
        step_into_opp = (nx, ny) in opp_terr
        step_into_uncl = (nx, ny) in unclaimed
        keep = 1 if (nx, ny) in self_terr else 0

        # Prefer expanding into unclaimed; capture opponent only if we are not overly behind.
        capture_bonus = 3.5 if step_into_opp and my_cnt >= opp_cnt else (2.0 if step_into_opp else 0.0)

        # Shape toward center and maintain boundary adjacency.
        sc = (-1.25 * dist_center) + (1.25 * step_into_uncl) + (1.0 * keep) + (1.0 * adj_our(nx, ny)) + capture_bonus
        # Slightly prefer moves that also reduce distance to opponent to contest center-play.
        sc += 0.15 * (abs(sx - ox) + abs(sy - oy) - (abs(nx - ox) + abs(ny - oy)))

        if sc > best_sc or (sc == best_sc and (dx, dy) < (best[0], best[1])):
            best_sc = sc
            best = [dx, dy]

    return [int(best[0]), int(best[1])]