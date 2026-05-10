def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def md(a, b, c, d):  # Manhattan
        da = a - c
        db = b - d
        if da < 0: da = -da
        if db < 0: db = -db
        return da + db

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = x, y  # engine would keep in place; model it
            dx, dy = 0, 0

        # Choose a target deterministically: maximize "I can deny/secure" while still near it.
        best_t = None
        best_t_val = -10**18
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Prefer resources where I'm closer, but still minimize absolute distance.
            t_val = (opd - myd) * 100 - myd
            if t_val > best_t_val:
                best_t_val = t_val
                best_t = (rx, ry)

        if best_t is None:
            continue

        # Secondary score: maximize how strongly the chosen target denies opponent.
        rx, ry = best_t
        myd = md(nx, ny, rx, ry)
        opd = md(ox, oy, rx, ry)
        final_val = (opd - myd) * 100 - myd

        # Tertiary deterministic tie-break: smaller dx, then smaller dy magnitude.
        if final_val > best_val:
            best_val = final_val
            best = (dx, dy)
        elif final_val == best_val and best is not None:
            if abs(dx) < abs(best[0]) or (abs(dx) == abs(best[0]) and abs(dy) < abs(best[1])):
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]