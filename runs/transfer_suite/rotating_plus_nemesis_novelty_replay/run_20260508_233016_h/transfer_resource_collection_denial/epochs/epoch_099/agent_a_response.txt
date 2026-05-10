def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    res_list = [(r[0], r[1]) for r in resources]
    res_set = set(res_list)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (-10**18, 0, 0, 0)
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # immediate value: prioritize collecting if present
        collect = 8.0 if (nx, ny) in res_set else 0.0

        # evaluate best contested resource after move
        local_best = (-10**18, None, None)
        for rx, ry in res_list:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)

            # want op_d - my_d large (we arrive earlier), slightly prefer nearer targets overall
            # and punish allowing opponent too close.
            diff = op_d - my_d
            val = diff * 3.0 - my_d * 0.15 - op_d * 0.03

            # add small boost when we would be clearly ahead
            if diff >= 2:
                val += 2.0
            # deterministic tie-break prefers lowest resource coordinates
            tie = (-val, rx, ry)
            if (val, -my_d, -op_d, -rx, -ry) > local_best[0:1] + ():
                local_best = (val, rx, ry)

        val = collect + local_best[0]

        # micro-tie: prefer staying away from obstacles by reducing distance to nearest obstacle
        mind = 0
        if obs_list:
            mind = min(cheb(nx, ny, ox2, oy2) for ox2, oy2 in obs_list)
            val += mind * 0.02

        # final deterministic tie-break
        key = (val, -abs(nx - ox), -abs(ny - oy), -rx if local_best[1] is not None else 0, -ry if local_best[2] is not None else 0, -dx, -dy)
        if key > best:
            best = key
            best_move = [dx, dy]

    return best_move