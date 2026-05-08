def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    best = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand

    if best is not None:
        return [best[1], best[2]]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand

    if best is None:
        return [0, 0]
    return [best[1], best[2]]