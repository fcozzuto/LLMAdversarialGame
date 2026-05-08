def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obst.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    def dist8(x1, y1, x2, y2):
        ax = abs(x1 - x2)
        ay = abs(y1 - y2)
        return ax if ax > ay else ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # Pick a resource by "race" priority: maximize lead (opponent distance - my distance).
    # If all bad (negative lead), choose the least bad and then closest.
    best_r = None
    best_key = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        lead = op_d - my_d
        key = (-lead, my_d, rx, ry)  # smaller -> better (lead high, then my close, then deterministic)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    best_move = (0, 0)
    best_mkey = None
    op_d_target = dist8(ox, oy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_d_after = dist8(nx, ny, tx, ty)
        lead_after = op_d_target - my_d_after
        # Prefer moves that increase/maintain advantage; then reduce distance to target.
        # Deterministic tie-breakers: prefer (0,0) earlier, then lex order.
        key = (-lead_after, my_d_after, dx, dy)
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]