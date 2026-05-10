def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (sx, sy)) or (sx, sy)

    def inside(x, y): 
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    self_set = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                self_set.add((x, y))

    opp_set = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                opp_set.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y) and (x, y) not in obstacles:
                unclaimed.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        d_opp = abs(nx - ox) + abs(ny - oy)
        sc += -2 * d_opp

        if (nx, ny) in opp_set:
            sc += 500  # flip opponent territory aggressively
        elif (nx, ny) in unclaimed:
            sc += 220  # claim unclaimed cells
        elif (nx, ny) in self_set:
            sc += 20   # avoid wandering too much

        # Prefer moving toward closest unclaimed (tie-break / shaping)
        if unclaimed:
            # local nearest among a small deterministic sample to keep fast
            sample = 0
            md = 10**9
            for (ux, uy) in unclaimed:
                dd = abs(nx - ux) + abs(ny - uy)
                if dd < md:
                    md = dd
                    sample = ux  # deterministic variable to avoid extra state
            sc += -3 * md

        # Obstacle safety and anti-stagnation
        if dx == 0 and dy == 0:
            sc -= 8

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]