def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for a in (observation.get("obstacles") or []):
        if isinstance(a, dict):
            if "x" in a and "y" in a:
                obs_set.add((int(a["x"]), int(a["y"])))
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            obs_set.add((int(a[0]), int(a[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, dict):
            if "x" in r and "y" in r:
                x, y = int(r["x"]), int(r["y"])
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
            resources.append((x, y))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        best = min(valid, key=lambda d: (abs((sx + d[0]) - ox) + abs((sy + d[1]) - oy), d[0] * 0 + d[1] * 0))
        return [int(best[0]), int(best[1])]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_target = None
    best_key = None
    for x, y in resources:
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        key = (ds - do, ds, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (x, y)

    tx, ty = best_target
    def eval_move(d):
        nx, ny = sx + d[0], sy + d[1]
        ds2 = man(nx, ny, tx, ty)
        do2 = man(nx, ny, ox, oy)
        # prioritize getting closer to target; then increase distance from opponent
        return (ds2, -do2, d[0], d[1])

    chosen = min(valid, key=eval_move)
    return [int(chosen[0]), int(chosen[1])]