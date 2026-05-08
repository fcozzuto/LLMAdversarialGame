def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def mobility(x, y):
        m = 0
        for a, b in dirs:
            x2, y2 = x + a, y + b
            if ok(x2, y2):
                m += 1
        return m

    def corner_metric(x, y):
        dx = min(x, (w - 1) - x)
        dy = min(y, (h - 1) - y)
        return min(dx, dy)  # smaller => closer to corner/wall

    best_move = [0, 0]
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy

        # Small, deterministic tie-breakers encourage stable behavior
        mob = mobility(nx, ny)
        center = -((nx - cx) ** 2 + (ny - cy) ** 2)
        corner = -corner_metric(nx, ny)

        # Wall-runner adaptation:
        # - If we are pursuer: slightly prefer moves that reduce opponent corner distance (force into tight area).
        # - If we are evader: slightly prefer moves that increase opponent distance and keep ourselves away from corners.
        opp_corner = -corner_metric(ox, oy)
        if is_evader:
            score = 1.6 * dist2 + 0.35 * mob + 0.10 * center - 0.20 * corner
        else:
            score = -1.8 * dist2 + 0.25 * mob + 0.06 * center + 0.12 * (-opp_corner) + 0.08 * corner

        # Key: primary score (higher better), then deterministic ordering by dx,dy pattern
        key = (round(score, 6), -abs(dx) - abs(dy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]