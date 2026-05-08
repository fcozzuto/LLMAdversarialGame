def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    def dist8(x1, y1, x2, y2):
        ax = abs(x1 - x2)
        ay = abs(y1 - y2)
        return ax if ax > ay else ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
        my_sep = abs(nx - ox) + abs(ny - oy)
        val = -10**18

        for rx, ry in resources:
            my_d = dist8(nx, ny, rx, ry)
            op_d = dist8(ox, oy, rx, ry)
            adv = op_d - my_d  # positive => we are closer
            # Prefer resources where we gain relative advantage; also keep some separation.
            cand = adv * 1000 - my_d * 3 + my_sep * 0.5
            if cand > val:
                val = cand

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]