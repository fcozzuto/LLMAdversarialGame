def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if is_free(nx, ny):
                val = -md(nx, ny, cx, cy)
                key = (val, -nx, -ny)
                if best_key is None or key > best_key:
                    best_key = key
                    best = [dx, dy]
        return best if best is not None else [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue
        my_best = -10**9
        my_closest = 10**9
        for rx, ry in resources:
            my_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            score = opp_d - my_d
            if score > my_best:
                my_best = score
                my_closest = my_d
            elif score == my_best and my_d < my_closest:
                my_closest = my_d
        # small bias: keep pressure by also preferring smaller my distance to the best-contested resource
        val = my_best - 0.02 * my_closest
        key = (val, -my_closest, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]