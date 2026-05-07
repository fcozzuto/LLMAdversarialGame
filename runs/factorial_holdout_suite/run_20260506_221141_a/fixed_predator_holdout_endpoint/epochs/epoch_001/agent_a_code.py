def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    x0, y0 = self_pos
    ox0, oy0 = opp_pos
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick best target: prefer resources where we are closer than opponent.
    best = None  # (target_x, target_y, self_d, opp_d)
    for rx, ry in resources:
        if not in_bounds(rx, ry):
            continue
        if (rx, ry) in obs_set:
            continue
        sd = manhattan((x0, y0), (rx, ry))
        od = manhattan((ox0, oy0), (rx, ry))
        # Higher means better for us (opponent relatively farther).
        key = (od - sd, -sd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry, sd, od)

    _, tx, ty, _, _ = best

    # Choose a move that reduces distance to target and avoids obstacles.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, None)  # (dist, order)
    order = 0
    for dx, dy in moves:
        nx, ny = x0 + dx, y0 + dy
        if not in_bounds(nx, ny):
            order += 1
            continue
        if (nx, ny) in obs_set:
            order += 1
            continue
        d = manhattan((nx, ny), (tx, ty))
        # Tie-break deterministically: smaller d, then prefer moves earlier in list.
        if best_move[0] is None or d < best_move[0]:
            best_move = (d, order)
        order += 1

    # If all moves invalid (rare), stay.
    if best_move[0] is None:
        return [0, 0]

    # Re-scan to pick the first move achieving best distance (deterministic).
    target_d = best_move[0]
    order = 0
    for dx, dy in moves:
        nx, ny = x0 + dx, y0 + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            order += 1
            continue
        d = manhattan((nx, ny), (tx, ty))
        if d == target_d:
            return [dx, dy]
        order += 1

    return [0, 0]