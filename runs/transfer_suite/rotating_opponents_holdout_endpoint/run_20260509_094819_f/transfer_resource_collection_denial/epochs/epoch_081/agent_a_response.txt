def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_move_for_target(tx, ty):
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obs:
                continue
            sd = abs(nx - tx) + abs(ny - ty)
            od = abs(nx - ox) + abs(ny - oy)
            adv = (abs(tx - ox) + abs(ty - oy)) - sd
            # prefer moves that keep adv high and bring closer to target
            key = (adv, -sd, -od)
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # Target selection: pick a resource where we are (currently) most ahead of opponent.
    best_target = None
    best_key = None
    for x, y in res:
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        key = (od - sd, -sd, -(abs(x - sx) + abs(y - sy)))
        if best_target is None or key > best_key:
            best_target, best_key = (x, y), key

    tx, ty = best_target
    mv = best_move_for_target(tx, ty)
    if mv == [0, 0]:
        # If blocked or no improving move, take a safe step that maximizes advantage locally.
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obs:
                continue
            # local advantage: relative distance to all resources
            adv_best = None
            for rx, ry in res:
                sd = abs(rx - nx) + abs(ry - ny)
                od = abs(rx - ox) + abs(ry - oy)
                val = od - sd
                if adv_best is None or val > adv_best:
                    adv_best = val
            key = (adv_best, -abs(nx - sx) - abs(ny - sy))
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]
    return mv