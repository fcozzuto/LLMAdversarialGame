def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("evade" in role) or ("runner" in role)

    if (sx, sy) == (ox, oy):
        return [0, 0]

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                candidates.append((0, 0))
            else:
                candidates.append((dx, dy))
    # deterministic ordering preference: towards horizontal/vertical first, then diagonals, then stay
    pref = {(1, 0):0, (-1, 0):0, (0, 1):0, (0, -1):0,
            (1, 1):1, (1, -1):1, (-1, 1):1, (-1, -1):1,
            (0, 0):2}

    best = None
    best_val = None

    # heuristic: if evader maximize distance and also avoid reducing it next step; if pursuer minimize distance
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = abs(ox - nx) + abs(oy - ny)
        # local mobility and obstacle pressure
        mobility = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                tx, ty = nx + ddx, ny + ddy
                if (ddx != 0 or ddy != 0) and ok(tx, ty):
                    mobility += 1
        # tie-breaker: prefer moves that don't step closer to the opponent if evader
        # and prefer stepping closer if pursuer.
        val = (dist, mobility)
        if is_evader:
            # lexicographic max on (dist, mobility), tie-break by preference
            key = (val[0], val[1], -pref[(dx, dy)])
            if best is None or key > best_val:
                best_val = key
                best = (dx, dy)
        else:
            # lexicographic min on distance: use negative dist for max compare
            key = (-val[0], val[1], -pref[(dx, dy)])
            if best is None or key > best_val:
                best_val = key
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]