def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None

    for tx, ty in resources:
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        can_win = 0 if sd < od else 1  # prefer resources we arrive strictly earlier
        diff = sd - od
        center_bias = abs(tx - cx) + abs(ty - cy)
        key = (can_win, diff, sd, center_bias, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    if tx == sx and ty == sy:
        return [0, 0]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        nx1, ny1 = sx + dx, sy
        if (nx1, ny1) not in obstacles and 0 <= nx1 < w and 0 <= ny1 < h:
            return [dx, 0]
        nx2, ny2 = sx, sy + dy
        if (nx2, ny2) not in obstacles and 0 <= nx2 < w and 0 <= ny2 < h:
            return [0, dy]
        return [0, 0]

    return [dx, dy]