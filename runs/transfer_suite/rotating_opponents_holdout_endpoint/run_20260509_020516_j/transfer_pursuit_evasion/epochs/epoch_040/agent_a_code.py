def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in (observation.get("obstacles") or []):
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("catcher" in role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist_m(nx, ny):
        return abs(nx - ox) + abs(ny - oy)

    # Evader target corners: opposite corners from pursuer (maximize distance).
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = (ox, oy)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d1 = dist_m(nx, ny)

        # 1-step lookahead to avoid walking into immediate capture when roles flip.
        # For pursuer: minimize opponent-next distance (w.r.t current opponent position).
        # For evader: maximize.
        # Since we don't know opponent move, we approximate with staying direction to own target.
        dtarget = abs(nx - tx) + abs(ny - ty)

        if is_pursuer:
            key = (-d1, dtarget, nx, ny)  # prefer closer to opponent (min d1), then nearer to opponent corner
            key = (-key[0], key[1], key[2], key[3])  # convert back to minimization on d1
            # Equivalent: (d1, dtarget, nx, ny)
            key = (d1, dtarget, nx, ny)
        else:
            key = (-d1, -dtarget, nx, ny)  # maximize d1 and dtarget
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]