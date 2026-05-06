def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def man(a, b, c, d):
        return abs(a - b) + abs(c - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best_t = resources[0]
    best_tv = None
    for tx, ty in resources:
        d_me = man(tx, x, ty, y)
        d_opp = man(tx, ox, ty, oy)
        lead = d_opp - d_me
        tv = lead * 2000 - d_me + 0.01 * d_opp
        if best_tv is None or tv > best_tv:
            best_tv = tv
            best_t = (tx, ty)
        elif tv == best_tv:
            d_me_b = man(best_t[0], x, best_t[1], y)
            if d_me < d_me_b:
                best_t = (tx, ty)

    tx, ty = best_t
    candidates = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        d_me = man(tx, nx, ty, ny)
        d_opp = man(tx, ox, ty, oy)
        lead = d_opp - d_me
        # Prefer moves that improve us' lead; slight preference to approach target fast.
        # Also include a small tie-break against moving into obstacle-adjacent squares.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if in_bounds(xx, yy) and blocked(xx, yy):
                    adj_obs += 1
        sc = lead * 2200 - d_me - 0.2 * adj_obs
        candidates.append((sc, d_me, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][2]), int(candidates[0][3])]