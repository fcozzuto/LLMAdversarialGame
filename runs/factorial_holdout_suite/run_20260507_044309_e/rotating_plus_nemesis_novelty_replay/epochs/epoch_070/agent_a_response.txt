def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obs_raw = observation.get("obstacles") or []
    obstacles = obs_raw if isinstance(obs_raw, set) else set(tuple(p) for p in obs_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0,  0), (1,  0),
             (-1,  1), (0,  1), (1,  1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            nx, ny = sx, sy
        if (nx, ny) in obstacles:
            nx, ny = sx, sy

        best_val_for_move = None
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Lead-first: maximize (opponent_time - self_time). Secondary: prefer nearer self and nearer overall.
            lead = do - ds
            cand = (lead, -ds, -(abs(rx - nx) + abs(ry - ny)), rx, ry)
            if best_val_for_move is None or cand > best_val_for_move:
                best_val_for_move = cand

        if best is None or best_val_for_move > best[0]:
            best = (best_val_for_move, dx, dy)

    return [best[1], best[2]] if best is not None else [0, 0]