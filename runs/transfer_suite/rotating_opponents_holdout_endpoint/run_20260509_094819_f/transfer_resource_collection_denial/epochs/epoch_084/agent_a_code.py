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

    def step_towards(tx, ty):
        dx = 0
        dy = 0
        if tx > sx:
            dx = 1
        elif tx < sx:
            dx = -1
        if ty > sy:
            dy = 1
        elif ty < sy:
            dy = -1
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]
        # fallback: try any delta that reduces manhattan distance and avoids obstacles
        best = None
        best_d = 10**9
        for mx, my in deltas:
            nx, ny = sx + mx, sy + my
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            d = abs(tx - nx) + abs(ty - ny)
            if d < best_d or (d == best_d and (mx, my) < best):
                best_d = d
                best = (mx, my)
        return list(best) if best is not None else [0, 0]

    best = None
    best_key = None
    for tx, ty in res:
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        # maximize advantage: prefer targets where opponent is relatively farther
        # If opponent is closer, still take if it is much better for us (break ties by our distance and position)
        key = (od - sd, -sd, -(tx + ty), tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    return step_towards(tx, ty)