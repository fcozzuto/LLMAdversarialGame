def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        myd = abs(rx - sx) + abs(ry - sy)
        opd = abs(rx - ox) + abs(ry - oy)
        adv = opd - myd
        key = (-adv, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            dist = abs(tx - nx) + abs(ty - ny)
            candidates.append((dist, dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Tie-break deterministically: prefer smaller dist, then prefer moves that are "more direct" toward target.
    best_c = None
    for dist, dx, dy, nx, ny in candidates:
        direct = -(abs(tx - (sx + dx)) + abs(ty - (sy + dy)))
        key = (dist, -direct, dx, dy)
        if best_c is None or key < best_c[0]:
            best_c = (key, [dx, dy])
    return best_c[1]