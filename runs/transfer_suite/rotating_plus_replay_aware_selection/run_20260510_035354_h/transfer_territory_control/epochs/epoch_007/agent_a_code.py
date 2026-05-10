def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (ax, ay))

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    unclaimed = observation.get("unclaimed_cells") or []
    un = [(x, y) for (x, y) in unclaimed if 0 <= x < w and 0 <= y < h] if unclaimed else []

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if un:
        tx, ty = min(un, key=lambda p: abs(p[0] - ax) + abs(p[1] - ay))
    else:
        tx, ty = (ox, oy) if (ox, oy) != (ax, ay) else (cx, cy)

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - ox) + abs(ny - oy)
        val = (d_t, -d_o, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = ax + dx, ay + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]