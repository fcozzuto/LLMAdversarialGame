def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy  # Chebyshev

    def move_toward(tx, ty, x, y):
        step_options = []
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        step_options.append((dx, dy))
        step_options.append((dx, 0))
        step_options.append((0, dy))
        step_options.append((0, 0))
        for mx, my in step_options:
            nx, ny = x + mx, y + my
            if legal(nx, ny):
                return [mx, my]
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        return move_toward(tx, ty, sx, sy)

    best = None  # (score, ds, rx, ry)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer resources we can win quickly; otherwise the closest one we can still contest.
        score = (ds - do, ds)
        cand = (score, ds, rx, ry)
        if best is None or cand < best:
            best = cand

    _, _, tx, ty = best
    return move_toward(tx, ty, sx, sy)