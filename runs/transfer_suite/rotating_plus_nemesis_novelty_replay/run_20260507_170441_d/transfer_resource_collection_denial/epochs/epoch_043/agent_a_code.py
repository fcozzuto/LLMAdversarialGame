def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(p[0], p[1]) for p in obstacles if p is not None}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Pick best target: prioritize closer to us, further from opponent; tie-break by coordinates.
    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        key = (my_d, op_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    rx, ry = best_t

    # Evaluate each possible move from our position.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_self = dist(nx, ny, rx, ry)
        d_op = dist(ox, oy, rx, ry)

        # Prefer moves that reach/approach target, keep opponent from reaching first.
        # Add obstacle-aware small penalty for being "stuck" (surrounded), to encourage progress.
        neigh_free = 0
        for mx, my in moves:
            tx, ty = nx + mx, ny + my
            if inb(tx, ty):
                neigh_free += 1
        stuck_pen = (8 - neigh_free) * 0.05

        lead_term = (d_op - d_self)  # positive if we are closer than opponent
        score = (d_self * 10.0) - (lead_term * 3.0) + stuck_pen

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]