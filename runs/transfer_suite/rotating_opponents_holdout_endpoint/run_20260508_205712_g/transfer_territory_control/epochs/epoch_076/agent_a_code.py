def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    sp = observation.get("self_position") or (0, 0)
    sx, sy = sp[0], sp[1]
    try:
        sx, sy = int(sx), int(sy)
    except:
        sx, sy = 0, 0

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    ox, oy = None, None
    if resources:
        bestd = None
        for x, y in resources:
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if bestd is None or d < bestd or (d == bestd and (x, y) < (ox, oy)):
                bestd = d
                ox, oy = x, y

    if ox is None:
        ox, oy = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        if resources:
            val = -(abs(nx - ox) + abs(ny - oy))
            if (nx, ny) in resources:
                val += 100000
        else:
            val = -(abs(nx - ox) + abs(ny - oy))
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]