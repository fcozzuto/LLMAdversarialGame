def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist8(x1, y1, x2, y2):
        ax = abs(x1 - x2)
        ay = abs(y1 - y2)
        return ax if ax > ay else ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # If no visible resources, move to reduce distance to opponent (denial pressure)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = dist8(nx, ny, ox, oy)
            key = (d, nx, ny)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return best[1] if best else [0, 0]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_best = None
        for rx, ry in resources:
            my_d = dist8(nx, ny, rx, ry)
            op_d = dist8(ox, oy, rx, ry)
            # Prefer resources we're closer to than the opponent; break ties by shortest my distance.
            adv = op_d - my_d
            key = (-adv, my_d, rx, ry)
            if my_best is None or key < my_best:
                my_best = key
        # Also bias toward staying near the opponent's current position if advantage is similar.
        opp_bias = dist8(nx, ny, ox, oy)
        top_key = (my_best, opp_bias, nx, ny)
        if best is None or top_key < best[0]:
            best = (top_key, (dx, dy))
    return best[1] if best else [0, 0]