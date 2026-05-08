def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    rset = set((r[0], r[1]) for r in resources)
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    bestv = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if (nx, ny) in rset:
            v = 10**12
        else:
            v = 0

        self_near = 10**18
        opp_near = 10**18
        best_competition = -10**18

        for rx, ry in resources:
            sd = d2(nx, ny, rx, ry)
            od = d2(ox, oy, rx, ry)
            if sd < self_near:
                self_near = sd
            if od < opp_near:
                opp_near = od
            # prefer positions that are relatively closer than opponent to some resource
            comp = od - sd
            if comp > best_competition:
                best_competition = comp

        # prioritize immediate pickup, then winning proximity race, then general closeness
        v += best_competition * 50
        v += (opp_near - self_near)
        v += (1 if nx == sx else 0) * -0.5  # mild nudge to move instead of idle when tied

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]