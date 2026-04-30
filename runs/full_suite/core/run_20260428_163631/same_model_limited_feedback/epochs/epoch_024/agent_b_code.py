def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = [(p[0], p[1]) for p in observation["resources"]]

    dxdy = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    # Choose target resource where we are relatively closer than opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        d1 = dist((sx, sy), (rx, ry))
        d2 = dist((ox, oy), (rx, ry))
        lead = d2 - d1
        # Prefer positive lead; break ties by smaller our distance, then by coordinate.
        key = (lead, -d1, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        best = (ox, oy)

    rx, ry = best

    # Evaluate next moves: approach target, avoid obstacles/out of bounds.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dxdy:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_our = dist((nx, ny), (rx, ry))
        d_cur = dist((sx, sy), (rx, ry))
        # Small deterministic tie-breakers toward center-ish and toward opponent direction.
        toward_center = - (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        toward_opp = - dist((nx, ny), (ox, oy))
        # Prefer moves that reduce our distance more, avoid stalling.
        delta = d_cur - d_our
        score = (delta, -d_our, toward_center, toward_opp, -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves were blocked, stay.
    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]