def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    cur_valid = 0 <= sx < w and 0 <= sy < h and (sx, sy) not in obs
    if not cur_valid:
        sx, sy = 0, 0

    if resources:
        target = None
        bestd = None
        for (rx, ry) in resources:
            d = man(sx, sy, rx, ry)
            if bestd is None or d < bestd:
                bestd = d
                target = (rx, ry)
        tx, ty = target
    else:
        tx, ty = ox, oy

    best_move = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obs:
            continue
        if resources:
            dres = man(nx, ny, tx, ty)
        else:
            dres = -man(nx, ny, tx, ty)
        dopp = man(nx, ny, ox, oy)
        val = (-dres * 100) + (dopp * 3)  # go for resource; avoid opponent slightly
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return best_move