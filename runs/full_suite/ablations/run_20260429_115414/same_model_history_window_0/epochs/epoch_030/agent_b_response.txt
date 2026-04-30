def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # Go to center if no resources visible
        tx, ty = w // 2, h // 2
    else:
        # Pick resource where we are relatively closer than opponent
        best = None
        best_val = None
        for rx, ry in resources:
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # Bias toward closer-to-us and farther-from-them
            val = (od - sd) * 10 - sd
            if best_val is None or val > best_val or (val == best_val and (rx, ry) < best):
                best_val = val
                best = (rx, ry)
        tx, ty = best

    # If target is blocked, retarget to nearest unblocked resource
    if (tx, ty) in obstacles:
        best = None
        bestd = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = dist((sx, sy), (rx, ry))
            if bestd is None or d < bestd or (d == bestd and (rx, ry) < best):
                bestd = d
                best = (rx, ry)
        if best is None:
            tx, ty = w // 2, h // 2
        else:
            tx, ty = best

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd_self = dist((nx, ny), (tx, ty))
        nd_opp = dist((nx, ny), (ox, oy))
        cur_self = dist((sx, sy), (tx, ty))
        cur_opp = dist((sx, sy), (ox, oy))
        # Prefer reducing distance to target, while not allowing opponent to get too close
        score = -nd_self * 5 + nd_opp * 0.3
        # Mildly prefer moves that improve relative position vs opponent distance to target
        if resources:
            oppd = dist((ox, oy), (tx, ty))
            rel_now = oppd - cur_self
            rel_after = oppd - nd_self
            score += (rel_after - rel_now) * 2
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]