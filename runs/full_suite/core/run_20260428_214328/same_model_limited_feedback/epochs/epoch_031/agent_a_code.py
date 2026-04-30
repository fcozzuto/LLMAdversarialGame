def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles or not inb(rx, ry):
                continue
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            gap = od - sd
            if best is None or gap > best[0] or (gap == best[0] and sd < best[1]):
                best = (gap, sd, rx, ry)
        tx, ty = best[2], best[3] if best else (ox, oy)
    else:
        tx, ty = ox, oy

    best_move = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        val -= md(nx, ny, tx, ty)
        val += 2 * md(nx, ny, ox, oy)
        if resources and (nx, ny) == (tx, ty):
            val += 1000
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move if best_move is not None else [0, 0]