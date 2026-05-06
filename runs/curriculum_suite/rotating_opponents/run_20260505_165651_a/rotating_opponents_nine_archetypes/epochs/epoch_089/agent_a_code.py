def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obs

    def mindist(x, y):
        best = 10**9
        for rx, ry in res:
            d = abs(x - rx) + abs(y - ry)
            if d < best:
                best = d
        return best if res else 10**9

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # Higher score is better: prefer nearer resources; add slight preference away from opponent.
        d_res = mindist(nx, ny)
        d_opp = abs(nx - ox) + abs(ny - oy)
        score = (-d_res * 3) + (d_opp * 0.15)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best_score == -10**18:
        return [0, 0]
    return [best[0], best[1]]