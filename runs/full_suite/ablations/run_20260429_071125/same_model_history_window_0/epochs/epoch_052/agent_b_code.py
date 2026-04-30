def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    # Choose resource where we are relatively closer than opponent
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Small tie-break favors nearer to opponent "pressure" being worse for them
        score = (sd - od * 0.85, sd)
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Evaluate candidate moves with obstacle and bounds, then approach target
    best_move = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd_target = dist((nx, ny), (tx, ty))
        nd_opp = dist((nx, ny), (ox, oy))
        # Encourage: closer to target, but also avoid giving opponent easy access
        # (if opponent is very close to target, prefer moves that increase opp distance)
        opp_to_target = dist((ox, oy), (tx, ty))
        pressure = 1.0 if opp_to_target <= 2 else 0.0
        val = (nd_target - 0.15 * nd_opp + pressure * (-0.35 * nd_opp), nd_target, -nd_opp)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]