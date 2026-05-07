def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)
    res_set = set((p[0], p[1]) for p in resources)

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a resource where we are most likely to arrive earlier than opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = man(sx, sy, rx, ry)
        op_d = man(ox, oy, rx, ry)
        # Prefer biggest "opponent advantage" (op_d - my_d), then smaller my_d.
        key = (op_d - my_d, -my_d, -(rx + 17 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        my_d2 = man(nx, ny, tx, ty)
        op_d2 = man(ox, oy, tx, ty)
        # If landing on a resource, prioritize heavily.
        gain = 1200 if (nx, ny) in res_set else 0
        # Encourage reducing distance and maintaining advantage over opponent.
        score = gain + (op_d2 - my_d2) * 10 - my_d2
        # Small deterministic bias to avoid oscillations: prefer staying on-grid and not moving backwards in x if tied.
        score += -0.01 * (abs(dx) + abs(dy)) - 0.001 * dx
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves were blocked, stay put.
    return [int(best_move[0]), int(best_move[1])]