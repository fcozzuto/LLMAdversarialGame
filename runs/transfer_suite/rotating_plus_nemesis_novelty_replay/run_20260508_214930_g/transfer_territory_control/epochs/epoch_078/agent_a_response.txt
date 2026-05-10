def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (7, 7))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),  (0, 0),  (0, 1),
            (1, -1),  (1, 0),  (1, 1)]

    base_my = abs(sx - ox) + abs(sy - oy)
    adj_opp = set()
    for dx, dy in dirs:
        ax, ay = ox + dx, oy + dy
        if ok(ax, ay):
            adj_opp.add((ax, ay))

    best = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 5000  # likely flip by entering
        if (nx, ny) in unclaimed:
            score += 60
        if (nx, ny) in self_t:
            score += 8

        # Prefer pushing toward opponent (while claiming space)
        nd = abs(nx - ox) + abs(ny - oy)
        score += (base_my - nd) * 4

        # Cut off opponent-adjacent squares; slightly prefer squares bordering opponent territory
        if (nx, ny) in adj_opp:
            score += 120
        neigh_opp = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty) and (tx, ty) in opp_t:
                neigh_opp += 1
        score += neigh_opp * 30

        # Keep away from our own weak spot: avoid stepping into the center if opponent is far
        if nd > 10 and (nx, ny) in self_t:
            score -= 5

        # Mild tie-breaker: prefer moving closer to board center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= int((abs(nx - cx) + abs(ny - cy)) * 0.1)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]