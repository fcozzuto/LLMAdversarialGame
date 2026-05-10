def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)

    obstacles = set()
    for x, y in (observation.get("obstacles") or []):
        if x is not None and y is not None:
            obstacles.add((int(x), int(y)))

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    frontier = set()
    if self_t:
        for ux, uy in unclaimed:
            for dx, dy in dirs8:
                if (ux + dx, uy + dy) in self_t:
                    frontier.add((ux, uy))
                    break

    def nearest_opp_dist(x, y):
        if not opp_t:
            return 99
        md = 99
        for ox, oy in opp_t:
            d = abs(x - ox) + abs(y - oy)
            if d < md:
                md = d
        return md

    def score_cell(nx, ny):
        if (nx, ny) in obstacles or not inb(nx, ny):
            return -10**9
        s = 0
        if (nx, ny) in opp_t:
            s += 8
        if (nx, ny) in self_t:
            s += 1
        if (nx, ny) in unclaimed:
            s += 3
        if (nx, ny) in frontier:
            s += 6
        if self_t and not frontier and (nx, ny) in unclaimed:
            s += 1
        d = nearest_opp_dist(nx, ny)
        s += (4 - d) * 0.7
        return s

    # If no self territory yet, head toward nearest unclaimed (deterministic).
    if not self_t:
        best = [0, 0]
        best_s = -10**9
        # choose via one-step look to minimize distance to nearest unclaimed
        targets = list(unclaimed) if unclaimed else (list(opp_t) if opp_t else [(sx, sy)])
        for dx, dy in dirs8:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # distance to closest target
            md = 99
            for tx, ty in targets:
                d = abs(nx - tx) + abs(ny - ty)
                if d < md:
                    md = d
            s = -md + (10 if (nx, ny) in opp_t else 0)
            if s > best_s:
                best_s = s
                best = [dx, dy]
        return best

    # Main policy: best scored neighboring cell.
    best = [0, 0]
    best_s = -10**9
    for dx, dy in dirs8:  # deterministic order
        nx, ny = sx + dx, sy + dy
        s = score_cell(nx, ny)
        if s > best_s:
            best_s = s
            best = [dx, dy]

    return best