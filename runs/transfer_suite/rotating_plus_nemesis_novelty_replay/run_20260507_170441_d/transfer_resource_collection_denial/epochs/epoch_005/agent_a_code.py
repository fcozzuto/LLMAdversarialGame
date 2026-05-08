def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {tuple(p) for p in obstacles}

    cand = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    def min_obst_dist2(x, y):
        md2 = 10**18
        for ox2, oy2 in obstacles:
            ddx = x - ox2
            ddy = y - oy2
            v = ddx * ddx + ddy * ddy
            if v < md2:
                md2 = v
        return 0 if md2 == 10**18 else md2

    if not resources:
        return [0, 0]

    # Opponent "nearest_resource" target
    r_op = min(resources, key=lambda r: (d2((ox, oy), r), r[0], r[1]))

    # We race a different resource (deny the opponent's immediate best)
    pool = [r for r in resources if r != r_op]
    target = None
    if pool:
        target = max(
            pool,
            key=lambda r: (d2(r, (ox, oy)) - d2(r, (sx, sy)), -d2(r, (sx, sy)), -r[0], -r[1]),
        )
    else:
        target = r_op

    best = [0, 0]
    bestv = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        selfd = d2((nx, ny), target)
        oppd = d2((ox, oy), target)
        # Encourage approaching target, penalize landing near obstacles, tie-break deterministically
        v = (oppd - selfd) - 0.02 * min_obst_dist2(nx, ny)
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best