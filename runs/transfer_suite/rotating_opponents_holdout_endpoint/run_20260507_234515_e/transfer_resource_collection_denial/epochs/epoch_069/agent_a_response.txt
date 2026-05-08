def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose resource we can secure: maximize (opp_time - self_time), then minimize self_time, then deterministic tie.
    best = None
    for rx, ry in res:
        dS = man(sx, sy, rx, ry)
        dO = man(ox, oy, rx, ry)
        # small bias to our side: deterministic and helpful vs "nearest resource" opponent
        our_half = (w - 1) / 2.0
        half_bias = -1 if (sx <= our_half and rx <= our_half) or (sx > our_half and rx >= our_half) else 0
        key = (dO - dS, -dS, half_bias, -rx, -ry)  # higher key is better
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    # Greedy step: among legal deltas, pick that minimizes distance to target; tie by maximizing distance to opponent.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                ds = man(nx, ny, tx, ty)
                do = man(nx, ny, ox, oy)
                candidates.append((ds, -do, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort()
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]