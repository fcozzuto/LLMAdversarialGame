def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d = dist2((nx, ny), (tx, ty))
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                best = (d, (dx, dy))
        return [best[1][0], best[1][1]] if best else [0, 0]

    my_best = None
    for rx, ry in resources:
        my_d = dist2((sx, sy), (rx, ry))
        op_d = dist2((ox, oy), (rx, ry))
        # Prefer resources I'm closer to; break ties by overall urgency (smaller my_d)
        score = (op_d - my_d, -my_d)
        if my_best is None or score > my_best[0] or (score == my_best[0] and (rx, ry) < my_best[1]):
            my_best = (score, (rx, ry))
    tx, ty = my_best[1]

    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        my_d = dist2((nx, ny), (tx, ty))
        op_d = dist2((ox, oy), (tx, ty))
        val = (op_d - my_d, -my_d)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]