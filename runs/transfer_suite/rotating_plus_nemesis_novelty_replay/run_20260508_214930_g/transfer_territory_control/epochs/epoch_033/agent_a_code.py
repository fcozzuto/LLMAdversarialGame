def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_self(nx, ny):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in self_t:
                    c += 1
        return c

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = (0, 0)
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        base = 0.0
        if (nx, ny) in opp_t:
            base -= 7.0  # avoid flipping into opponent territory
        elif (nx, ny) in unclaimed:
            base += 4.0  # claim forward territory
        elif (nx, ny) in self_t:
            base += 1.5  # consolidate
        else:
            base += 0.5  # safety/neutral

        a = adj_self(nx, ny)
        base += a * 2.0

        # keep pressure toward open space, away from immediate opponent
        dist_opp = abs(nx - ox) + abs(ny - oy)
        base += dist_opp * (-0.06)

        # slight center preference to reduce corner trapping
        dist_ctr = abs(nx - cx) + abs(ny - cy)
        base += dist_ctr * (-0.01)

        # discourage staying still if there is a clearly better claim
        if dx == 0 and dy == 0:
            base -= 0.2

        if base > best_s:
            best_s = base
            best = (dx, dy)

    return [int(best[0]), int(best[1])]