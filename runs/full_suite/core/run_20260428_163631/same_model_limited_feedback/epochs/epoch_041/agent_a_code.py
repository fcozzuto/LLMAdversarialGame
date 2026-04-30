def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]

    obs_set = set((x, y) for x, y in obstacles)
    res_set = set((x, y) for x, y in resources)

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    # Deterministic tie-breaking order: prefer straight, then staying.
    candidates = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            # keep preferred order: (0,0) last among same score by adding bias
            candidates.append((dx, dy))

    def manh(a, b, c, d):
        d1 = a - c
        if d1 < 0:
            d1 = -d1
        d2 = b - d
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    def best_resource_dist(px, py):
        md = 10**9
        for rx, ry in resources:
            d = abs(px - rx) + abs(py - ry)
            if d < md:
                md = d
        return md if resources else 10**6

    opp_dist_now = manh(sx, sy, ox, oy)

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in candidates:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            score = -10**12
        else:
            res_bonus = 600 if (nx, ny) in res_set else 0
            dist_res = best_resource_dist(nx, ny)
            # Encourage moving toward resources and away from opponent.
            dist_opp = manh(nx, ny, ox, oy)
            # Small preference to keep options open (avoid getting boxed) using obstacle adjacency.
            adj_obs = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    if adx == 0 and ady == 0:
                        continue
                    ax = nx + adx
                    ay = ny + ady
                    if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs_set:
                        adj_obs += 1
            score = (
                res_bonus
                - 12 * dist_res
                + 4 * dist_opp
                + (2 if dist_opp > opp_dist_now else 0)
                - 20 * adj_obs
            )
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]