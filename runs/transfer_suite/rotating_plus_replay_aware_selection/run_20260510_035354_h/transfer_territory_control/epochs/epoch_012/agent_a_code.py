def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation.get("opponent_position", (ax, ay))
    obstacles_in = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_in:
        try:
            x, y = p
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    best = None
    best_s = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_op = abs(nx - ox) + abs(ny - oy)
        d_c = abs(nx - cx) + abs(ny - cy)
        s = (-d_op) + (-(0.01 * d_c))
        if best_s is None or s > best_s:
            best_s = s
            best = (dx, dy)
        elif s == best_s and best is not None:
            if (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]