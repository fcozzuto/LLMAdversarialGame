def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if (sx, sy) in obstacles:
        obstacles.discard((sx, sy))
    if (ox, oy) in obstacles:
        obstacles.discard((ox, oy))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in cand:
            v = man(nx, ny, tx, ty) - man(nx, ny, ox, oy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = None
    bestv = None
    for dx, dy, nx, ny in cand:
        best_res = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            val = ds - (1 if ds <= do else 0) * 2
            if best_res is None or val < best_res:
                best_res = val
        opp_close = man(nx, ny, ox, oy)
        v = best_res + 0.01 * opp_close
        if bestv is None or v < bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]