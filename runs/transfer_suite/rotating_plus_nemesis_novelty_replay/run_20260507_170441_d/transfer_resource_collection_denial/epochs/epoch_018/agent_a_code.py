def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    # Pick target resource that benefits us relative to opponent.
    best_r = None
    best_adv = None
    best_myd = None
    for rx, ry in resources:
        myd = d2(sx, sy, rx, ry)
        opd = d2(ox, oy, rx, ry)
        adv = opd - myd  # positive => opponent farther
        if (best_r is None or adv > best_adv or (adv == best_adv and myd < best_myd) or
            (adv == best_adv and myd == best_myd and (rx, ry) < best_r)):
            best_r, best_adv, best_myd = (rx, ry), adv, myd

    rx, ry = best_r
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    opd = d2(ox, oy, rx, ry)

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2_new = d2(nx, ny, rx, ry)
        # Maximize our advantage after move.
        val = (opd - myd2_new) * 10 - myd2_new
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    if best_val is None:
        # No legal moves except maybe stay; ensure deterministic return.
        if valid(sx, sy):
            return [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best_move