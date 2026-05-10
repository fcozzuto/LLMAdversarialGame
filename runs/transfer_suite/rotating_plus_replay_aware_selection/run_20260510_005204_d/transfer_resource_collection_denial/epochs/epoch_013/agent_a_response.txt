def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cd(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    if not resources:
        return [0, 0]

    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    # Choose resource where we have positional advantage; avoid obstacles via move filtering later.
    best_target = None
    best_key = None
    for rx, ry in resources:
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        diff = opd - myd  # higher => we are closer or opponent is farther
        center_bias = -(abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
        key = (diff, -myd, center_bias, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    res_set = set((p[0], p[1]) for p in resources)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in res_set:
            val = (10**9, 0, 0)
        else:
            n_my = cd(nx, ny, tx, ty)
            n_op = cd(ox, oy, tx, ty)
            adv = n_op - n_my
            val = (adv, -n_my, -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]