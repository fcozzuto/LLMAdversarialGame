def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    oset = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or ("catch" in role) or ("hunter" in role)
    if not is_pursuer:
        is_pursuer = ("evader" not in role)

    resources = observation.get("resources", []) or []
    rset = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in oset:
                rset.append((x, y))

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in oset:
            return -10**18
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        # obstacle "soft" repulsion
        if oset:
            mind = 10**9
            for (px, py) in oset:
                dd = (nx - px) * (nx - px) + (ny - py) * (ny - py)
                if dd < mind:
                    mind = dd
            obs_term = mind
        else:
            obs_term = 10**6

        # resource bias (very small; primarily avoid capture)
        if rset:
            rmin = 10**9
            for (rx, ry) in rset:
                dd = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if dd < rmin:
                    rmin = dd
            res_term = -rmin
        else:
            res_term = 0

        if is_pursuer:
            return (-d2) + 0.001 * obs_term + 0.0001 * res_term
        else:
            return (d2) + 0.001 * obs_term + 0.0001 * res_term

    best_dx, best_dy = 0, 0
    best_v = -10**18
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in deltas:
        v = score_move(dx, dy)
        if v > best_v:
            best_v = v
            best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]