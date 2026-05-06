def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not res:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = sx + dx, sy + dy
                    if free(nx, ny):
                        return [dx, dy]
        return [0, 0]

    # Choose target we can reach first (or at least with best margin), then closest to us.
    best = None
    best_key = None
    for x, y in res:
        sd = md(sx, sy, x, y)
        od = md(ox, oy, x, y)
        adv = od - sd  # higher is better
        key = (-adv, sd, x, y)  # negate adv to use min consistently
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    cur_sd = md(sx, sy, tx, ty)
    cur_od = md(ox, oy, tx, ty)
    best_move = [0, 0]
    best_move_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        nsd = md(nx, ny, tx, ty)
        # If we move closer but opponent would also get closer relative to us, penalize.
        ndiff = (cur_od - nsd)  # updated advantage margin relative to fixed opponent
        # Prefer reducing our distance; lightly penalize staying still.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        key = (0 - ndiff, nsd, stay_pen, x := nx, y := ny, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]