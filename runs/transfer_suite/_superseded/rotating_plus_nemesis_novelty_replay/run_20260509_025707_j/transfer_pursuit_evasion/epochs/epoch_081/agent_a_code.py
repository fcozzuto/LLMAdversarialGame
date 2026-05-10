def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role) or ("evasion" in role)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res = observation.get("resources") or []
    best_step = (0, 0)
    best_score = None

    rx = ry = None
    if res:
        dmin = None
        for t in res:
            if isinstance(t, (list, tuple)) and len(t) >= 2:
                x, y = int(t[0]), int(t[1])
                if not valid(x, y):
                    continue
                d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
                if dmin is None or d < dmin:
                    dmin = d
                    rx, ry = x, y

    def score(nx, ny):
        dx1 = nx - sx
        dy1 = ny - sy
        move_pen = 0 if (dx1 == 0 and dy1 == 0) else 0.01
        if rx is not None:
            d_self = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
            d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            if i_am_evader:
                return d_self * -1 + d_opp * 0.02 + -move_pen
            return d_self * -1 + d_opp * -0.01 + -move_pen
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if i_am_evader:
            return d_opp * 1 + -move_pen
        d_self = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        return d_self * -1 + -move_pen

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = score(nx, ny)
        if best_score is None or sc > best_score:
            best_score = sc
            best_step = (dx, dy)

    dx, dy = best_step
    return [int(dx), int(dy)]