def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(p[0], p[1]) for p in obstacles if p is not None}

    def king(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose best target: prefer ones we can reach earlier; else ones where we deny opponent more.
    best = None
    for rx, ry in resources:
        my_d = king(sx, sy, rx, ry)
        op_d = king(ox, oy, rx, ry)
        # want smallest (my-op deficit) and, secondarily, smallest my distance
        key = (my_d - op_d, my_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # If very close to opponent, add a slight bias to move toward cells that worsen opponent progress.
    opp_close = king(sx, sy, ox, oy) <= 2

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        my_new = king(nx, ny, tx, ty)
        op_new = king(ox, oy, tx, ty)
        # Move value: reduce my distance first; if opponent is also close, deny by increasing their next advantage.
        # Deterministic tie-break by coordinates.
        if opp_close:
            opp_bias = -king(nx, ny, ox, oy)  # prefer staying closer to opponent to contest
            key = (my_new, -op_new, opp_bias, nx, ny)
        else:
            key = (my_new, my_new - op_new, nx, ny)
        if best_move is None or key < best_move[0]:
            best_move = (key, (dx, dy))

    if best_move is None:
        return [0, 0]
    return [int(best_move[1][0]), int(best_move[1][1])]