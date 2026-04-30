def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # Move to reduce distance to opponent slightly while staying safe
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            sc = dist((nx, ny), (ox, oy))
            if sc < best[0] or (sc == best[0] and (nx, ny) < (best[1], best[2])):
                best = (sc, nx, ny)
        return [best[1] - sx, best[2] - sy]

    # Choose target resource where we are relatively closer than opponent (deterministic tie-breakers)
    opp_pos = (ox, oy)
    self_pos = (sx, sy)
    best_t = None
    best_key = None
    for r in resources:
        tx, ty = r[0], r[1]
        if (tx, ty) in obstacles:
            continue
        ds = dist(self_pos, (tx, ty))
        do = dist(opp_pos, (tx, ty))
        key = (ds - do, ds, tx + ty, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)
    tx, ty = best_t

    # Evaluate moves: go toward target, keep distance from opponent, avoid obstacles near by
    def min_obs_d(nx, ny):
        md = 10**9
        for obx, oby in obstacles:
            d = abs(nx - obx) + abs(ny - oby)
            if d < md:
                md = d
                if md == 0:
                    return 0
        return md if md != 10**9 else 99

    best_sc = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_t = dist((nx, ny), (tx, ty))
        d_o = dist((nx, ny), (ox, oy))
        # Encourage intercept: prefer moves that reduce our advantage gap and keep opponent farther
        ds0 = dist(self_pos, (tx, ty))
        do0 = dist(opp_pos, (tx, ty))
        gap0 = ds0 - do0
        gap1 = d_t - d_o
        obs_d = min_obs_d(nx, ny)
        sc = (gap1, d_t, -d_o, -obs_d, nx, ny)
        if best_sc is None or sc < best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]