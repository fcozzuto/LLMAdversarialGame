def choose_move(observation):
    w = int(observation.get("grid_width", 1) or 1)
    h = int(observation.get("grid_height", 1) or 1)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    ob = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.add((int(p[0]), int(p[1])))

    res = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            res.append((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_options(x, y):
        out = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in ob:
                out.append((dx, dy, nx, ny))
        if not out:
            return [(0, 0, x, y)]
        return out

    opts = step_options(sx, sy)

    if res:
        best = None
        for dx, dy, nx, ny in opts:
            d = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)
            key = (d, abs(ox - nx) + abs(oy - ny), dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    best = None
    for dx, dy, nx, ny in opts:
        d = abs(nx - ox) + abs(ny - oy)
        key = (d, -dx, -dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]