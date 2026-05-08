def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    unclaimed = observation.get("unclaimed_cells") or []
    best = None
    best_key = None

    for p in unclaimed:
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if x == sx and y == sy:
            continue
        d_self = abs(x - sx) + abs(y - sy)
        d_opp = abs(x - ox) + abs(y - oy)
        key = (d_opp, d_self, x, y)
        if best is None or key < best_key:
            best = (x, y)
            best_key = key

    if best is None:
        resources = observation.get("resources") or []
        rbest = None
        rkey = None
        for p in resources:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            d_self = abs(x - sx) + abs(y - sy)
            key = (d_self, x, y)
            if rbest is None or key < rkey:
                rbest = (x, y)
                rkey = key
        best = rbest
        if best is None:
            best = (w // 2, h // 2)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    if dx == 0 and dy == 0:
        if sx > 0:
            dx = -1
        elif sx < w - 1:
            dx = 1
        elif sy > 0:
            dy = -1
        elif sy < h - 1:
            dy = 1
        else:
            dx = dy = 0

    return [dx, dy]