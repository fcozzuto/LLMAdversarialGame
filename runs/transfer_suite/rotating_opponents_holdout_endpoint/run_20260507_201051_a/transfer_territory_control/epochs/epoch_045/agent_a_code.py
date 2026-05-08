def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = list(map(tuple, observation.get("resources") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        targets = resources
    elif unclaimed:
        targets = unclaimed
    else:
        targets = [(ox, oy)]

    def best_dist(x, y):
        d = 10**9
        for t in targets:
            dt = manh((x, y), t)
            if dt < d:
                d = dt
        return d

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = best_dist(nx, ny)
        sc = -2 * d
        if (nx, ny) in opp_t:
            sc += 220
        if (nx, ny) in self_t:
            sc += 20
        if (nx, ny) in obstacles:
            sc -= 10**7
        if resources and (nx, ny) in set(resources):
            sc += 400
        if (not resources) and unclaimed and (nx, ny) in set(unclaimed):
            sc += 260
        sc += -manh((nx, ny), (ox, oy)) // 3
        if sc > best_score or (sc == best_score and (dx, dy) < (best[0], best[1]) if best else False):
            best_score = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]