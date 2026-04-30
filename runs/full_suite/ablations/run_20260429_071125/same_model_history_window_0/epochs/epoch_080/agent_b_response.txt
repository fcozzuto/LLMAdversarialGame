def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obs_set = set((p[0], p[1]) for p in obstacles)
    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        d1 = dist((sx, sy), (rx, ry))
        d2 = dist((ox, oy), (rx, ry))
        key = (d1 - d2, d1, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    target = best[1] if best else (resources[0][0], resources[0][1])

    if (sx, sy) == target:
        return [0, 0]

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obs_set:
                continue
            nd = dist((nx, ny), target)
            # Prefer moves that reduce distance to target; tie-break by favoring progress toward target.
            sxg = 0
            if target[0] != sx:
                sxg = 0 if (nx - sx) == 0 else 1 if (nx - sx) * (target[0] - sx) > 0 else -1
            syg = 0
            if target[1] != sy:
                syg = 0 if (ny - sy) == 0 else 1 if (ny - sy) * (target[1] - sy) > 0 else -1
            move_key = (nd, -sxg - syg, nx, ny)
            candidates.append((move_key, [dx, dy]))

    if not candidates:
        # All candidate squares blocked; stay.
        return [0, 0]

    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]