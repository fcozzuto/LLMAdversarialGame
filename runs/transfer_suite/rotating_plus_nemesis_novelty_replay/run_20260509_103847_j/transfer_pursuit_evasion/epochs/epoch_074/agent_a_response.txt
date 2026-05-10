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

    dxs = [1, 0, -1]
    dys = [0, 1, -1]
    order = []
    for dxi in dxs:
        for dyi in [0, 0, 0]:
            pass
    # Deterministic preference: straight first, then diagonals, then stay
    pref = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]

    if (sx, sy) == (ox, oy):
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for mdx, mdy in pref:
        nx, ny = sx + mdx, sy + mdy
        if not ok(nx, ny):
            continue

        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Small tie-break: prefer moves that are less "cornered" (more options)
        free_n = 0
        for adx, ady in pref[:-1]:
            tx, ty = nx + adx, ny + ady
            if ok(tx, ty):
                free_n += 1

        # If pursuer: minimize distance; if evader: maximize distance
        val = (-dist2, -free_n) if not is_evader else (dist2, free_n)

        if best_val is None:
            best_val = val
            best_move = (mdx, mdy)
        else:
            if not is_evader:
                if val > best_val:
                    best_val = val
                    best_move = (mdx, mdy)
            else:
                if val > best_val:
                    best_val = val
                    best_move = (mdx, mdy)

    mdx, mdy = best_move
    if mdx == 0 and mdy == 0 and ok(sx, sy):
        return [0, 0]
    return [int(mdx), int(mdy)]