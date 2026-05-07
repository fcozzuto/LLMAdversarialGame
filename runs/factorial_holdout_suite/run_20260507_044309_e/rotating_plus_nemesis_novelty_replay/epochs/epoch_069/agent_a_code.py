def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we are ahead (do - ds). If behind, prefer less-losing / nearer.
        val = (do - ds, -ds, rx, ry)
        candidates.append((val, rx, ry))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: t[0], reverse=True)
    _, tx, ty = candidates[0]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0),
             (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            return [int(mdx), int(mdy)]
    return [0, 0]