def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # Intercept-aware greedy: pick the move that creates the best overall "reach priority"
    # where our distance is compared against opponent's distance to the same resource.
    best = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue
        my_to = []
        for rx, ry in resources:
            my_d = dist8(nx, ny, rx, ry)
            op_d = dist8(ox, oy, rx, ry)
            # Prefer resources we can reach no later than opponent; otherwise prefer to reduce the gap.
            # Use deterministic tie-break by (op_d, rx, ry).
            reach = 1000000 - my_d if my_d <= op_d else (op_d - my_d)
            my_to.append((reach, -my_d, op_d, rx, ry))
        my_to.sort()
        # Choose best resource for this move, then pick move with best resource-priority.
        rkey = my_to[0]
        # Sort order: higher reach, then closer to resource, then opponent farther, then stable coordinates.
        move_key = (-rkey[0], rkey[1], rkey[2], rkey[3], rkey[4], dxm, dym)
        if best is None or move_key < best:
            best = move_key
            best_move = [dxm, dym]

    return best_move