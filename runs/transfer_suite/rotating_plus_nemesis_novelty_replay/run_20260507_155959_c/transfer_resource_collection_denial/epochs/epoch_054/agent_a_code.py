def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]
    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target_self = min(res, key=lambda r: (md(sx, sy, r[0], r[1]), r[0], r[1]))
    target_opp = min(res, key=lambda r: (md(ox, oy, r[0], r[1]), r[0], r[1]))

    tx, ty = target_self
    ox_t, oy_t = target_opp
    step_ox = 0 if ox == ox_t else (1 if ox_t > ox else -1)
    step_oy = 0 if oy == oy_t else (1 if oy_t > oy else -1)
    pred = (ox + step_ox, oy + step_oy)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dself = md(nx, ny, tx, ty)
        deny = 1 if (nx, ny) == pred else 0
        # Key: maximize deny, then minimize distance to own target, then deterministic tie-break
        key = (deny, -dself, -abs(nx - sx) - abs(ny - sy), nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]