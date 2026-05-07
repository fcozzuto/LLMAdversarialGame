def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []) or [])

    def in_bounds(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    valid = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        # Deterministic fallback: drift toward center
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if x == tx else (1 if x < tx else -1)
        dy = 0 if y == ty else (1 if y < ty else -1)
        if (x + dx, y + dy) in obstacles:
            return [0, 0]
        return [dx, dy]

    best_move = (0, 0)
    best_val = None

    for dx, dy in valid:
        nx, ny = x + dx, y + dy
        # Choose the resource where we gain the most "tempo" over the opponent after moving.
        best_for_move = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            my_d = abs(rx - nx) + abs(ry - ny)
            op_d = abs(rx - ox) + abs(ry - oy)
            # Prefer larger op_d - my_d (earlier capture), then smaller my_d, then deterministic resource tie.
            val = (op_d - my_d, -my_d, -(rx + ry), -rx, -ry)
            if best_for_move is None or val > best_for_move:
                best_for_move = val
        if best_val is None or best_for_move > best_val:
            best_val = best_for_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]