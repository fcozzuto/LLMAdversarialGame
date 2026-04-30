def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        obs.add((p[0], p[1]))
    res = []
    for r in resources:
        res.append((r[0], r[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def obs_pen(x, y):
        p = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obs:
                p += 1
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If standing on a resource, stay (or effectively capture); deterministic.
    for rx, ry in res:
        if sx == rx and sy == ry:
            return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        if (nx, ny) in set(res):
            return [dx, dy]

        # Evaluate by selecting the resource that maximizes our distance advantage.
        if res:
            local_best = -10**18
            for rx, ry in res:
                d_self = man(nx, ny, rx, ry)
                d_opp = man(ox, oy, rx, ry)
                # If we're closer than opponent, strongly prefer; otherwise still move toward best contest.
                val = (d_opp - d_self) * 10.0 - d_self * 0.6 - obs_pen(nx, ny) * 0.9
                # Mild bias toward center to avoid dead-ends.
                val -= (abs(nx - cx) + abs(ny - cy)) * 0.03
                if val > local_best:
                    local_best = val
        else:
            # No resources left: move to reduce opponent's mobility pressure while keeping legal.
            local_best = -(man(nx, ny, ox, oy)) - obs_pen(nx, ny) * 2.0

        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]