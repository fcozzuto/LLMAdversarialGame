def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_gain = -10**18
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        gain = (od - sd) * 1000 - sd  # prioritize winning race, then closer
        # small tie-break: prefer resources nearer to our "front" direction from start corner
        front = (rx + ry) if (sx + sy) <= (w - 1 + h - 1 - sx - sy) else (2 * (w - 1) + 2 * (h - 1) - rx - ry)
        gain += -0.001 * front
        if gain > best_gain:
            best_gain = gain
            best = (rx, ry)
    tx, ty = best

    def move_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            return -10**18
        sd_after = man(nx, ny, tx, ty)
        # Denial: if we can also align to potentially cut off nearby resources, prefer reduced distance to any resource.
        min_res = 10**9
        for rx, ry in resources:
            dd = man(nx, ny, rx, ry)
            if dd < min_res:
                min_res = dd
        return -sd_after * 10 - min_res + (0 if (nx, ny) == (sx, sy) else 0)

    best_move = (0, 0)
    best_ms = -10**18
    for dx, dy in deltas:
        ms = move_score(dx, dy)
        if ms > best_ms:
            best_ms = ms
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]