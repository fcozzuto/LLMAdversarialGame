def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    res_list = [(r[0], r[1]) for r in resources]

    def in_bounds(x, y):
        return 0 <= x < W and 0 <= y < H

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    best_delta = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose the resource that this move makes us best positioned for.
        local_best = -10**18
        for rx, ry in res_list:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Advantage: higher means opponent is further from that resource.
            adv = do - ds
            # Slightly prefer closer resources to avoid dithering.
            closeness = -0.1 * ds
            # Prefer avoiding "dead" cells near obstacles.
            adj_obs = 0
            if (nx + 1, ny) in obstacles:
                adj_obs += 1
            if (nx - 1, ny) in obstacles:
                adj_obs += 1
            if (nx, ny + 1) in obstacles:
                adj_obs += 1
            if (nx, ny - 1) in obstacles:
                adj_obs += 1
            score = 2.0 * adv + closeness - 0.25 * adj_obs
            if score > local_best:
                local_best = score

        # If all resources are equally bad, tie-break by staying closer to nearest resource.
        if local_best > best_score:
            best_score = local_best
            best_delta = [dx, dy]

    # If every move was blocked, stay.
    if best_delta == [0, 0] and (sx, sy) in obstacles:
        return [0, 0]
    return best_delta