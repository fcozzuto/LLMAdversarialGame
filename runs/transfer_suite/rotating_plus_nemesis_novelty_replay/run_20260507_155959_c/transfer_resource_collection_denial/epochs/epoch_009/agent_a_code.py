def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    res_set = set(res)
    best = None
    best_score = -10**30

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        score = 0

        if (nx, ny) in res_set:
            score += 1000000  # immediate pickup

        # Antidenial: strongly prefer positions that keep/extend lead to a resource.
        # Also lightly prefer moving toward the best overall resource.
        local_best = -10**30
        for rx, ry in res:
            d_self = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            lead = d_op - d_self  # positive => we are closer than opponent currently (from next)
            if d_self == 0:
                local_best = 10**12
                break
            cand = 1200 * lead - 8 * d_self  # deny opponent by maximizing lead
            if cand > local_best:
                local_best = cand
        score += local_best
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]