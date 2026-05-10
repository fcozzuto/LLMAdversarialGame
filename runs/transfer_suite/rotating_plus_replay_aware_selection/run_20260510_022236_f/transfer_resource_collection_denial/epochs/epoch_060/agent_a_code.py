def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)
    res = [(int(x), int(y)) for x, y in resources if 0 <= int(x) < w and 0 <= int(y) < h and (int(x), int(y)) not in obs]
    if not res:
        return [0, 0]
    if (sx, sy) in set(res):
        return [0, 0]

    def man(a, b, x, y):
        return abs(a - x) + abs(b - y)

    def adj_obs_pen(x, y):
        pen = 0
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs:
                pen += 1
        return pen

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        pen = adj_obs_pen(nx, ny)
        # Evaluate the best resource we can aim for after this move.
        val = -10**18
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Big weight to being earlier than opponent; small tie to quick pickup.
            v = (od - sd) * 100 - sd - pen * 0.75
            if v > val:
                val = v
        # Prefer staying closer to the opponent's closest reachable resource to disrupt denial.
        if len(res) >= 2:
            cr = min(res, key=lambda p: man(ox, oy, p[0], p[1]))
            sd2 = man(nx, ny, cr[0], cr[1])
            od2 = man(ox, oy, cr[0], cr[1])
            val += (od2 - sd2) * 2
        if val > best_val:
            best_val = val
            best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]