def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    obs_raw = observation.get("obstacles") or []
    obstacles = obs_raw if isinstance(obs_raw, set) else set(tuple(p) for p in obs_raw)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = None
    best_sec = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep us in place

        # One-step lookahead: maximize our best "arrival margin" over all resources.
        # value = (opponent_distance - our_distance) after the move; higher is better.
        local_best = None
        local_ds = None
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = do - ds
            if local_best is None or val > local_best or (val == local_best and (local_ds is None or ds < local_ds or (ds == local_ds and (rx, ry) < local_best_pt))):
                local_best = val
                local_ds = ds
                local_best_pt = (rx, ry)

        # Second criterion: prefer overall closeness if margins tie.
        sec = local_ds if local_ds is not None else 10**9

        if best_val is None or local_best > best_val or (local_best == best_val and sec < best_sec) or (local_best == best_val and sec == best_sec and (dx, dy) < best_move):
            best_val = local_best
            best_sec = sec
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]