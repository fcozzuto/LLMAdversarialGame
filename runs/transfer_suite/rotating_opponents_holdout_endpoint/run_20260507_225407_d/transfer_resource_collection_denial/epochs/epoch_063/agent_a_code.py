def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            x, y = int(x), int(y)
            if inb(x, y):
                obs.add((x, y))
        except Exception:
            pass

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    res_list = observation.get("resources") or []
    resources = []
    for p in res_list:
        try:
            x, y = p
            x, y = int(x), int(y)
            if ok(x, y):
                resources.append((x, y))
        except Exception:
            pass

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    if not ok(sx, sy) or not resources:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if ok(nx, ny):
                    return [dx, dy]
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        key = (od - sd, -sd)  # prefer winning resources, then closer to finish
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Local move selection with obstacle safety: maximize expected advantage after the move
    best_move = [0, 0]
    best_move_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            sd = md(nx, ny, tx, ty)
            od = md(ox, oy, tx, ty)
            key = (od - sd, -sd)
            if best_move_key is None or key > best_move_key:
                best_move_key = key
                best_move = [dx, dy]

    return best_move