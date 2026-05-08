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
        dx = x1 - x2
        dy = y1 - y2
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    def best_for_move(nx, ny):
        if not resources:
            d = man(nx, ny, ox, oy)
            return (0, -d, 0, nx, ny)  # purely move to be close to opponent when idle
        best = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # We want to be closer than opponent and also generally closer to reduce absolute time
            adv = od - sd
            key = (adv, -sd, -sd - man(nx, ny, rx, ry) * 0, rx, ry)
            if best is None or key > best:
                best = key
        return best

    best_key = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        key = best_for_move(nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move