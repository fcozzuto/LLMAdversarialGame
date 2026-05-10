def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = dirs

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(cset, x, y):
        c = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in cset:
                c += 1
        return c

    base = abs(sx - ox) + abs(sy - oy)
    best = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 5000
        elif (nx, ny) in unclaimed:
            score += 120
        else:
            score += 10 if (nx, ny) in self_t else 0

        self_adj = adj_count(self_t, nx, ny)
        opp_adj = adj_count(opp_t, nx, ny)

        score += 35 * self_adj
        score -= 55 * opp_adj

        # Prefer moving toward expanding our reach while keeping distance from opponent area
        d_opp = abs(nx - ox) + abs(ny - oy)
        score += (d_opp - base) * 2

        # Small tie-break to reduce dithering: prefer staying near same heading (deterministic)
        score += -0.1 * (abs(dx) + abs(dy))

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]