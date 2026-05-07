def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        try:
            x, y = p
            obstacles.add((x, y))
        except Exception:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_r = None
    best_key = None
    for r in resources:
        try:
            rx, ry = r
        except Exception:
            continue
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, (rx + ry) % 2, -rx + ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    tx, ty = best_r
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    options = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, 0), (0, -dy)]
    for mx, my in options:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mx), int(my)]

    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [int(mx), int(my)]

    return [0, 0]