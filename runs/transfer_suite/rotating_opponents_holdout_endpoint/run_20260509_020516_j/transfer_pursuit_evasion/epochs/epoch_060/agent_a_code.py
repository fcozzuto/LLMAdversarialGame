def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_evader = ("evader" in self_role) or (opp_role and "pursuer" in opp_role) or ("pursuit" in self_role and "evade" in self_role)

    dirs = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if i_am_evader:
        target_corner = None
        corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
        # Prefer corner farthest from opponent; deterministic tie-break by order above
        bestc = -10**9
        for c in corners:
            d = (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy)
            if d > bestc:
                bestc = d
                target_corner = c

        def score(nx, ny):
            # primary: distance from opponent; secondary: distance to chosen far corner
            d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            d_corner = (nx - target_corner[0]) * (nx - target_corner[0]) + (ny - target_corner[1]) * (ny - target_corner[1])
            return (d_opp, d_corner, -abs(nx - sx) - abs(ny - sy))

        best_move = (0, 0)
        best_sc = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            sc = score(nx, ny)
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # If we're pursuer/chaser: move to reduce Chebyshev distance; avoid obstacles
    def score(nx, ny):
        d1 = max(abs(nx - ox), abs(ny - oy))
        # Break ties by reducing Manhattan and favoring moves that align diagonally
        d2 = abs(nx - ox) + abs(ny - oy)
        diag_bonus = (1 if (nx != sx and ny != sy) else 0)
        return (-d1, -d2, diag_bonus, -abs(nx - sx) - abs(ny - sy))

    best_move = (0, 0)
    best_sc = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sc = score(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]