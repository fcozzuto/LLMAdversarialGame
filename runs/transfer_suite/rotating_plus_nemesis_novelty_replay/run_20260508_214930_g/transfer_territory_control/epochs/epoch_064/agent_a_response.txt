def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    n8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def frontier_score(x, y):
        c = 0
        for dx, dy in n8:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) in unclaimed:
                    c += 1
                elif (nx, ny) in opp_t:
                    c += 1 if (nx, ny) not in self_t else 0
        return c

    base = abs(sx - ox) + abs(sy - oy)
    best = (0, 0)
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sc = 0

        if (nx, ny) in opp_t:
            sc += 8000
        elif (nx, ny) in unclaimed:
            sc += 220
        elif (nx, ny) in self_t:
            sc += 20

        sc += 35 * frontier_score(nx, ny)

        nd = abs(nx - ox) + abs(ny - oy)
        sc += (base - nd) * 6  # prefer getting closer to opponent while sweeping

        # avoid being boxed-in: count free neighboring cells
        free = 0
        for ddx, ddy in n8:
            tx, ty = nx + ddx, ny + ddy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                free += 1
        sc += free * 2

        # mild bias to keep expanding outward from opponent side
        sc += (nx - ox) * 0.3 + (ny - oy) * 0.1

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]