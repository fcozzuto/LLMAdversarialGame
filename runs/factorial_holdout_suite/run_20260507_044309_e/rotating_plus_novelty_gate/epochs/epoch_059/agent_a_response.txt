def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (w // 2, h // 2)
        best = None
        for dx, dy, nx, ny in valid:
            k = (cheb(nx, ny, tx, ty), nx, ny, dx, dy)
            if best is None or k < best:
                best = k; bestmv = (dx, dy)
        return [bestmv[0], bestmv[1]]

    res = sorted((r[0], r[1]) for r in resources)
    res_set = set(res)

    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in valid:
        bonus = -1 if (nx, ny) in res_set else 0
        best_diff = None
        best_d = None
        best_rx = 0
        best_ry = 0
        for rx, ry in res:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            diff = d1 - d2
            if best_diff is None or diff < best_diff or (diff == best_diff and (d1 < best_d or (d1 == best_d and (rx, ry) < (best_rx, best_ry)))):
                best_diff = diff
                best_d = d1
                best_rx, best_ry = rx, ry
        # Prefer (more negative diff), then smaller own distance, then on-resource, then lexicographic stability.
        key = (best_diff, best_d, -bonus, best_rx, best_ry, nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]