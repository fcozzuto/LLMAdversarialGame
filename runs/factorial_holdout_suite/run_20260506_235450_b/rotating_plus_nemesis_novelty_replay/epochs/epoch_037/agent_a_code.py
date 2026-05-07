def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list if len(p) >= 2)
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resources = observation.get("resources", []) or []
    resources_xy = [(p[0], p[1]) for p in resources if len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = None
    if resources_xy:
        bestd = 10**9
        for r in resources_xy:
            d = man((sx, sy), r)
            if d < bestd or (d == bestd and r < target):
                bestd, target = d, r
    else:
        target = (0, h - 1) if sx < w // 2 else (w - 1, 0)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = 0
        if resources_xy:
            score -= man((nx, ny), target) * 5
        else:
            score -= man((nx, ny), target)
        score -= man((nx, ny), (ox, oy)) * 2
        if (nx, ny) == (ox, oy):
            score -= 10**6
        if (nx, ny) in resources_xy:
            score += 1000
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score, best_move = score, (dx, dy)
    if valid(sx, sy):
        return [best_move[0], best_move[1]]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]