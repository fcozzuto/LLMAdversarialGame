def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_value(x, y):
        best = -10**18
        for rx, ry in resources:
            sd = man(x, y, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources where we're ahead and closer to collecting.
            # Also heavily punish moving away too much.
            lead = od - sd
            v = 10 * lead - sd
            if v > best:
                best = v
        return best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        penalty = 0
        if (nx, ny) in obstacles:
            penalty = 10**9
        score = cell_value(nx, ny) - penalty
        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]