def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_score = -10**18
    base_dist = abs(sx - ox) + abs(sy - oy)

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue
        score = 0
        if (nx, ny) in opp_t:
            score += 2000
        elif (nx, ny) in unclaimed:
            score += 40
        if (nx, ny) in self_t:
            score += 10
        nd = abs(nx - ox) + abs(ny - oy)
        score += (nd - base_dist) * 2
        score += (1 if (nx, ny) in self_t else 0)
        score -= (1 if (nx, ny) in opp_t else 0)
        if score > best_score:
            best_score = score
            best = (ddx, ddy)

    if best is not None:
        return [best[0], best[1]]
    return [0, 0] if ok(sx, sy) else [1, 0] if ok(sx + 1, sy) else [-1, 0] if ok(sx - 1, sy) else [0, 1] if ok(sx, sy + 1) else [0, -1] if ok(sx, sy - 1) else [0, 0]