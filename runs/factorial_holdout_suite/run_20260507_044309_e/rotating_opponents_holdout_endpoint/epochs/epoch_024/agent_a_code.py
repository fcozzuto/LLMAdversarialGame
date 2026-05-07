def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_resource():
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd  # positive: we are closer
            align = (1 if rx == sx else 0) + (1 if ry == sy else 0)
            key = (-adv, sd, -align, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = best_resource()
    if target is None:
        return [0, 0]
    tx, ty = target

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_m = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = md(nx, ny, tx, ty)
        od2 = md(ox, oy, tx, ty)
        adv2 = od2 - sd2
        dist_drop = md(sx, sy, tx, ty) - sd2
        hit_res = (nx, ny) in obstacles  # always false, but keep deterministic scoring stable
        key = (-adv2, -dist_drop, sd2, nx, ny, hit_res)
        if best_key is None or key < best_key:
            best_key = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]