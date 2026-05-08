def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

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

    if not ok(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if ok(nx, ny):
                    return [dx, dy]
        return [0, 0]

    if not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_target = None
    best_val = None
    for tx, ty in resources:
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        val = (od - sd, -sd)  # prefer steal advantage; then closer
        if best_val is None or val > best_val:
            best_val = val
            best_target = (tx, ty)

    tx, ty = best_target
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_sd = md((sx, sy), (tx, ty))
    cur_od = md((ox, oy), (tx, ty))
    best_move = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nsd = abs(nx - tx) + abs(ny - ty)
        # opponent pressure estimate: assume opponent also moves toward same target (one step)
        nod = cur_od  # baseline
        # tie-break: prefer reducing our distance; and avoid moves that would be "too slow" vs opponent
        steal_gain = (cur_od - cur_sd) - (nod - nsd)
        key = (-(nsd), steal_gain, -(abs(nx - ox) + abs(ny - oy)))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]