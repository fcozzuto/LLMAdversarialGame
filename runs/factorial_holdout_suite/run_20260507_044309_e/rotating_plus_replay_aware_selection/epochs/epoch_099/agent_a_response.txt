def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    ox, oy = observation["opponent_position"]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def step_toward(tx, ty, x, y):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        nx, ny = x + dx, y + dy
        if legal(nx, ny):
            return [dx, dy]
        nx, ny = x + dx, y
        if legal(nx, ny):
            return [dx, 0]
        nx, ny = x, y + dy
        if legal(nx, ny):
            return [0, dy]
        # deterministic local detour
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if legal(nx, ny):
                    if cheb(nx, ny, tx, ty) < cheb(x, y, tx, ty):
                        return [ddx, ddy]
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        return step_toward(tx, ty, sx, sy)

    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we're much closer AND opponent is not.
        value = (do - ds) * 10 - ds
        tie = (rx, ry)
        cand = (value, tie, do, ds)
        if best is None or cand > best:
            best = cand

    if best is None:
        # all resources blocked (unlikely)
        tx, ty = w // 2, h // 2
        return step_toward(tx, ty, sx, sy)

    _, _, _, ds_best = best
    # Recover target deterministically by matching ds_best among max value/resources
    # (still deterministic; avoids storing extra state)
    target = None
    target_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        if ds != ds_best and target is None:
            continue
        do = cheb(ox, oy, rx, ry)
        value = (do - ds) * 10 - ds
        if target is None or value > target_val or (value == target_val and (rx, ry) < target):
            target = (rx, ry)
            target_val = value

    if target is None:
        target = min(resources, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))
    tx, ty = target
    return step_toward(tx, ty, sx, sy)