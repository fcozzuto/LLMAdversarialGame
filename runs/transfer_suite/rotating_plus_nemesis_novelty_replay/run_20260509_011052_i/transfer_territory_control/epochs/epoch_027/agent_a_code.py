def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj4_count(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        d_opp = abs(ox - x) + abs(oy - y)
        center_bias = -0.12 * (abs(cx - x) + abs(cy - y))
        a_self = adj4_count(x, y, self_terr)
        a_opp = adj4_count(x, y, opp_terr)
        if (x, y) in opp_terr:
            # capturing opponent territory on entry is strong, but avoid places surrounded by opponent
            return 7.0 + 1.5 * a_self - 1.0 * a_opp + 0.03 * d_opp + center_bias
        if (x, y) in unclaimed:
            # expand outward from our frontier toward center
            return 6.0 + 2.0 * a_self - 0.8 * a_opp - 0.02 * d_opp + center_bias
        if (x, y) in self_terr:
            # keep building cohesion on our side while still drifting to center
            return 2.0 + 0.7 * a_self - 0.6 * a_opp + 0.02 * d_opp + center_bias
        return -1.0 * (abs(cx - x) + abs(cy - y))

    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_cell(nx, ny)
        # deterministic tie-break: prefer closer to center, then smaller dx, then smaller dy
        if v > bestv or (v == bestv and (abs(cx - nx) + abs(cy - ny), dx, dy) < (abs(cx - (sx + best[0])) + abs(cy - (sy + best[1])), best[0], best[1])):
            bestv = v
            best = [dx, dy]
    return [int(best[0]), int(best[1])]