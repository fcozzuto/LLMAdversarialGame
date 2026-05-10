def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles", []) or []
    obs = {tuple(p) for p in obstacles if p is not None and len(p) >= 2}

    resources = observation.get("resources", []) or []
    res = [tuple(p) for p in resources if p is not None and len(p) >= 2]
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory", []) or []) if p is not None and len(p) >= 2)
    self_t = set(tuple(p) for p in (observation.get("self_territory", []) or []) if p is not None and len(p) >= 2)
    un = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []) if p is not None and len(p) >= 2)

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def nearest_res(x, y):
        if not res:
            return 0
        bestd = 10**9
        for rx, ry in res:
            d = man(x, y, rx, ry)
            if d < bestd:
                bestd = d
        return bestd

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        dres = nearest_res(nx, ny)
        dprop = man(nx, ny, ox, oy)

        score = -dres
        if (nx, ny) in self_t:
            score += 3
        if (nx, ny) in opp_t:
            score -= 6
        if (nx, ny) in un:
            score += 2
        score -= dprop * 0.15

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move == [0, 0] and (sx, sy) in obs:
        return [0, 0]
    return best_move