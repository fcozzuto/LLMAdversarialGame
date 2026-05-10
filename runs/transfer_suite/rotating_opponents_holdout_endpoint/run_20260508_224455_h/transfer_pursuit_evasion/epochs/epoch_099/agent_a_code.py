def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax >= ay else ay

    def min_obst_dist(x, y):
        best = 10**9
        for (px, py) in obs_set:
            d = cheb(x, y, px, py)
            if d < best:
                best = d
        return best if best != 10**9 else 99

    role = (observation.get("self_role") or "").lower()
    want_evade = ("evader" in role) or ("evading" in role) or ("runner" in role) or ("evasion" in role)

    best_val = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        od = min_obst_dist(nx, ny)
        # Prefer open space; for evader also prioritize larger opponent distance.
        if want_evade:
            val = (d * 1000) + (od * 10) - (abs(nx - sx) + abs(ny - sy))
        else:
            val = (-d * 1000) + (od * 10) - (abs(nx - sx) + abs(ny - sy))  # lower d better
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move