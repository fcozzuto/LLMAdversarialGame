def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    blocked = set((x, y) for x, y in obstacles)
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    deltas.sort(key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target selection: prefer resources where we are relatively closer than opponent.
    best_t = None
    best_gain = -10**9
    for rx, ry in resources:
        if (rx, ry) in blocked:
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        gain = (od - sd) * 10 - sd
        # small deterministic nudge: prefer lower coordinates on ties
        if gain > best_gain or (gain == best_gain and (rx, ry) < best_t):
            best_gain = gain
            best_t = (rx, ry)

    # If no viable resources, drift away from opponent toward safer region (corner bias).
    if best_t is None:
        target = (w - 1, h - 1) if (sx + sy) < (ox + oy) else (0, 0)
    else:
        target = best_t

    # Opponent response: when close, prioritize moves that increase separation while still heading to target.
    sep = dist((sx, sy), (ox, oy))
    want_separation = sep <= 3

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue
        d_to_t = dist((nx, ny), target)
        d_to_o = dist((nx, ny), (ox, oy))
        # primary: reduce distance to target
        score = -d_to_t * 100
        # secondary: contest behavior relative to opponent for the same target
        if best_t is not None:
            cur_sd = dist((sx, sy), target)
            cur_od = dist((ox, oy), target)
            next_gain = (cur_od - d_to_t) * 10 - d_to_t
            score += next_gain
        if want_separation:
            score += d_to_o * 25
        # discourage stepping adjacent to obstacles (soft)
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in blocked:
                    adj_pen += 1
        score -= adj_pen * 3

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]