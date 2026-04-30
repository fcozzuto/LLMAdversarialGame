def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    turn = observation["turn_index"]
    rem = observation.get("remaining_resource_count", len(resources))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        # Chebyshev distance (works well with diagonal moves)
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick a deterministic target resource: alternate between nearest-to-self and "pressure" targets
    if resources:
        if (turn + rem) % 2 == 0:
            best = min(resources, key=lambda p: (dist((sx, sy), p), p[0], p[1]))
        else:
            # Prefer resources that are closer to self but also keep farther from opponent
            best = min(resources, key=lambda p: (dist((sx, sy), p) - 0.35 * dist((ox, oy), p), -p[0], -p[1]))
    else:
        best = (sx, sy)

    best_move = [0, 0]
    best_val = -10**18
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res_set = set(tuple(p) for p in resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        new_pos = (nx, ny)
        gain = 0
        if (nx, ny) in res_set:
            gain = 1000 + 2 * (w + h)

        to_target = dist(new_pos, best)
        to_opp = dist(new_pos, (ox, oy))

        # Obstacle avoidance: penalize moves that come closer to obstacles
        obs_pen = 0
        if obstacles:
            md = 10**9
            for ox2, oy2 in obstacles:
                md = min(md, dist(new_pos, (ox2, oy2)))
            obs_pen = 8.0 / (1 + md)

        # If resources are dwindling, prioritize reaching any resource; otherwise prioritize target
        if rem <= 4 and resources:
            nearest_any = min(dist(new_pos, p) for p in resources)
            val = gain + 9.0 / (1 + nearest_any) + 0.08 * to_opp - obs_pen
        else:
            val = gain + 10.0 / (1 + to_target) + 0.06 * to_opp - obs_pen

        # Deterministic tie-break: prefer smaller dx, then dy, then stability
        tie = (val == best_val)
        if val > best_val or (tie and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]