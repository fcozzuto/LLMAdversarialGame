def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [tuple(p) for p in (observation.get("resources") or [])]
    if (sx, sy) in obstacles:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in valid:
            d = abs(nx - tx) + abs(ny - ty)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    opp_pos = (ox, oy)
    res_set = set(resources)
    best = None
    for dx, dy, nx, ny in valid:
        my_pos = (nx, ny)
        my_nearest = None
        score = -10**9
        for r in res_set:
            my_d = abs(nx - r[0]) + abs(ny - r[1])
            op_d = abs(ox - r[0]) + abs(oy - r[1])
            # Prefer taking resources where we can arrive earlier, else minimize distance.
            s = (op_d - my_d) * 2 - my_d
            if op_d < my_d:
                s -= 5  # don't chase hopeless ones
            if my_nearest is None or my_d < my_nearest:
                my_nearest = my_d
            if s > score:
                score = s
        # Tie-break: avoid unnecessary drift and bias toward earlier arrival distance.
        key = (-score, my_nearest, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]