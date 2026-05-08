def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}
    resources = observation.get("resources") or []

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if resources:
        target = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
        best = None
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            key = (man(nx, ny, target[0], target[1]), -man(nx, ny, ox, oy))
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    best = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        key = (man(nx, ny, ox, oy), -man(nx, ny, sx, sy))
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [best[0], best[1]]