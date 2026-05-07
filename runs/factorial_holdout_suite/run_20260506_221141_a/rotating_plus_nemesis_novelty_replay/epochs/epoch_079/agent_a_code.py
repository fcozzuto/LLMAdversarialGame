def choose_move(observation):
    def get_pos(key):
        p = observation.get(key, (0, 0))
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        return 0, 0

    sx, sy = get_pos("self_position")
    ox, oy = get_pos("opponent_position")
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    obs = observation.get("obstacles") or []
    for it in obs:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh:
                obstacles.add((x, y))

    resources = []
    res = observation.get("resources") or []
    for it in res:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    def step_toward(tx, ty):
        dx = tx - sx
        dy = ty - sy
        dx = 1 if dx > 0 else (-1 if dx < 0 else 0)
        dy = 1 if dy > 0 else (-1 if dy < 0 else 0)
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obstacles:
            # try axis move
            candidates = [(dx, 0), (0, dy), (-dx, 0), (0, -dy), (0, 0)]
            for cx, cy in candidates:
                nx, ny = sx + cx, sy + cy
                if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                    return [cx, cy]
            return [0, 0]
        return [dx, dy]

    if resources:
        best = None
        bestd = 10**18
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                best = (rx, ry)
        return step_toward(best[0], best[1])

    # No visible resources: move to reduce proximity to opponent
    target_x = 0 if ox > sx else gw - 1
    target_y = 0 if oy > sy else gh - 1
    return step_toward(target_x, target_y)