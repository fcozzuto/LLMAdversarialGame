def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (7, 7)

    obstacles = set()
    for x, y in (observation.get("obstacles") or []):
        if x is not None and y is not None:
            obstacles.add((int(x), int(y)))

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_unclaimed_count(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                c += 1
        return c

    # If opponent is pressing, prioritize flipping their cells; otherwise expand to unclaimed frontier.
    opp_press = 0
    if opp_t:
        # distance to closest opponent-territory cell
        md = 99
        for ax, ay in opp_t:
            d = abs(sx - ax) + abs(sy - ay)
            if d < md:
                md = d
        opp_press = 1 if md <= 3 else 0

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            # engine will reject; staying in place may be better than going out/into obstacle
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                continue

        if (nx, ny) in opp_t:
            base = 120 if opp_press else 95
        elif (nx, ny) in unclaimed:
            base = 45
        elif (nx, ny) in self_t:
            base = 10
        else:
            base = 5

        # expansion value: how many unclaimed cells are adjacent (more mobility/claims)
        exp = 6 * neigh_unclaimed_count(nx, ny)

        # avoid stepping too close to opponent unless we are flipping
        dist_opp = abs(nx - ox) + abs(ny - oy)
        if (nx, ny) in opp_t:
            prox = max(0, 6 - dist_opp) * 2
            safety = dist_opp * 0.2
            sc = base + exp + prox + safety
        else:
            safety = max(0, 7 - dist_opp) * -6
            sc = base + exp + safety

        # slight preference to keep moving toward center to reduce edge trapping
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bonus = -0.5 * (abs(nx - cx) + abs(ny - cy))
        sc += center_bonus

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]