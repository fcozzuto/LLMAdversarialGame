def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def cheb(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    cx, cy = w // 2, h // 2
    tx, ty = cx, cy
    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (ds - do, ds, abs(rx - cx) + abs(ry - cy), rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        if best is not None:
            tx, ty = best[1], best[2]

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]
    best_move = (0, 0)
    best_key = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        key = (ds - do, ds, abs(tx - nx) + abs(ty - ny), abs(nx - cx) + abs(ny - cy), mx, my)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]