def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (w - 1, h - 1))
    try:
        sx, sy = int(sp[0]), int(sp[1])
    except:
        sx, sy = 0, 0
    try:
        ox, oy = int(op[0]), int(op[1])
    except:
        ox, oy = w - 1, h - 1

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_d = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = abs(nx - ox)
        dyv = abs(ny - oy)
        if dyv > d:
            d = dyv
        if d < best_d:
            best_d = d
            best = (dx, dy)
        elif d == best_d and best is not None:
            if (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]