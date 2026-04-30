def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    if (sx, sy) in set((x, y) for x, y in resources):
        return [0, 0]

    cand_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res_set = set((x, y) for x, y in resources)
    if not res_set:
        # No resources visible: move to maximize distance from opponent deterministically
        best = None
        best_obj = None
        for dx, dy in cand_moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            obj = -(abs(nx - ox) + abs(ny - oy)) + (nx + ny) * 1e-6
            if best_obj is None or obj < best_obj:
                best_obj = obj
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose target resource by contesting: prefer resources where we're relatively closer than opponent
    best_target = None
    best_t = None
    for rx, ry in res_set:
        md = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        t = md - 0.5 * od + 0.001 * (rx + ry)
        if best_t is None or t < best_t:
            best_t = t
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = (0, 0)
    best_obj = None
    for dx, dy in cand_moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(nx, ny, ox, oy)
        # Minimize distance to target while keeping away from opponent
        obj = myd + 0.2 * opd + 0.0001 * (nx + 2 * ny)
        if best_obj is None or obj < best_obj:
            best_obj = obj
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]