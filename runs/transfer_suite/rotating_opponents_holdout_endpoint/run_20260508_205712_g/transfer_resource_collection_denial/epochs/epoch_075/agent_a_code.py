def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Try to drift away from opponent while staying safe
        best = (10**9, 0, 0)
        ret = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            key = (-d2, dx, dy)
            if key < best:
                best, ret = key, [dx, dy]
        return ret

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target resources where we are relatively faster; also add a slight preference to break ties by
    # pushing along the axis where we are ahead (helps vs row-sweepers).
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obs:
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        advantage = od - sd
        ax_ahead = (1 if rx > sx else -1 if rx < sx else 0) * (1 if ox < rx else -1 if ox > rx else 0)
        # Favor moves that change x when we have an advantage in x direction.
        x_step_bias = abs(rx - sx) > abs(ry - sy)
        key = (
            -advantage,                      # larger advantage first
            sd,                              # then smaller self distance
            0 if x_step_bias else 1,         # then prefer x-focused when close
            -ax_ahead,                       # deterministic minor bias
            ((rx + 17 * ry) % 13),          # stable ordering
            rx, ry
        )
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    # Compute desired step (diagonal allowed), but choose among safe deltas that improve our "target score".
    desired_dx = 0 if rx == sx else (1 if rx > sx else -1)
    desired_dy = 0 if ry == sy else (1 if ry > sy else -1)

    def target_score(nx, ny):
        sd2 = md(nx, ny, rx, ry)
        od2 = md(ox, oy, rx, ry)
        # Prefer improving our advantage; if equal, reduce distance to target; then approach opponent slightly less.
        adv = od2 - sd2
        return (-adv, sd2, -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)))

    best = None
    ret = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        s = target_score(nx, ny)
        # Encourage moving toward the target (especially diagonally) but only if it doesn't require unsafe logic.
        bias = (0 if dx == desired_dx else 1) + (0 if dy == desired_dy else 1)
        key = (s, bias, dx, dy)
        if best is None or key < best:
            best, ret = key, [dx, dy]
    return ret