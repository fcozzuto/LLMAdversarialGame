def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        dx = 1 if ox < sx else (-1 if ox > sx else 0)
        dy = 1 if oy < sy else (-1 if oy > sy else 0)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if in_bounds(nx, ny) and (nx, ny) not in obstacles else [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer resources closer than opponent; otherwise prefer still closest/efficient
        takeover = 0 if ds <= do else 1
        # Tie-break toward center and slightly toward reducing ds
        center_bias = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        key = (takeover, ds, center_bias, rx, ry, do)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx_options = (-1, 0, 1)
    dy_options = (-1, 0, 1)
    candidates = []
    for dx in dx_options:
        for dy in dy_options:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), (tx, ty))
            # Avoid moving into opponent range (reduce chance of immediate contest)
            opp_d = dist((nx, ny), (ox, oy))
            score_key = (d, 0 if (opp_d >= 2) else 1, -opp_d, dx, dy)
            candidates.append((score_key, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]