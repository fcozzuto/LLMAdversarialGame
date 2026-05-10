def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    target = None
    best_td = 10**9
    for cx, cy in unclaimed:
        if (cx, cy) in self_t or (cx, cy) in opp_t:
            continue
        adj_opp = False
        for ax, ay in neigh8:
            if (cx + ax, cy + ay) in opp_t:
                adj_opp = True
                break
        if not adj_opp:
            continue
        d = abs(cx - sx) + abs(cy - sy)
        if d < best_td or (d == best_td and (cy, cx) < (target[1], target[0]) if target else True):
            best_td = d
            target = (cx, cy)

    if target is None and unclaimed:
        target = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[1], p[0]))

    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if (nx, ny) in opp_t:
            score += 10000
        if (nx, ny) in unclaimed:
            score += 200
        if (nx, ny) in self_t:
            score += 10
        if target is not None:
            score += -2 * (abs(nx - target[0]) + abs(ny - target[1]))
            score += 3 * (abs(sx - target[0]) + abs(sy - target[1]) - (abs(nx - target[0]) + abs(ny - target[1])))
        if (dx, dy) == (0, 0) and target is not None:
            score -= 25
        score += -0.1 * (abs(nx - ox) + abs(ny - oy))
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]