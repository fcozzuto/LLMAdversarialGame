def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def move_value(nx, ny):
        if not resources:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            return -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        my_op_dist = man(nx, ny, ox, oy)
        # Prefer moving to resources where we can arrive earlier, else deny where opponent is closer.
        best = -10**9
        for rx, ry in resources:
            dm = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            advantage = do - dm  # positive is good (we are closer)
            # Strongly favor contests we can win; still allow denying slightly worse resources.
            val = advantage * 8.0 - dm * 0.35 + (advantage > 0) * 2.5
            # If too close to opponent, lightly discourage.
            val -= max(0, 4 - my_op_dist) * 0.3
            if val > best:
                best = val
        # If any immediate resource capture possible, guarantee it.
        for rx, ry in resources:
            if nx == rx and ny == ry:
                best = 10**8
                break
        return best

    best_move = [0, 0]
    best_val = -10**18
    # Deterministic tie-break by fixed order in moves
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = move_value(nx, ny)
        if v > best_val + 1e-12:
            best_val = v
            best_move = [dx, dy]
    return best_move