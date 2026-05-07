def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best = None
    for r in resources:
        if (r[0], r[1]) in obstacles:
            continue
        d_self = dist2((sx, sy), r)
        d_opp = dist2((ox, oy), r)
        # Prefer resources closer to us and relatively farther from opponent
        key = (d_self - d_opp, d_self, -r[0], -r[1])
        if best is None or key < best[0]:
            best = (key, r)
    target = best[1]

    dx = 0
    dy = 0
    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            myd = dist2((nx, ny), target)
            opd = dist2((ox, oy), target)
            # Primary: reduce distance to target; Secondary: don't let opponent be closer by much
            val = (myd, (myd - opd), abs(nx - target[0]) + abs(ny - target[1]), -nx, -ny)
            candidates.append((val, (mx, my)))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda z: z[0])
    return [int(candidates[0][1][0]), int(candidates[0][1][1])]