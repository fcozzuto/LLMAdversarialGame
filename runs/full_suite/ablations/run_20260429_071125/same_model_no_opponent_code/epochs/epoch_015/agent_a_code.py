def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obs = {(p[0], p[1]) for p in obstacles}

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        best_key = None
        for p in resources:
            rx, ry = p[0], p[1]
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer a resource where we can reach no later than opponent.
            key = (-(sd <= od), (od - sd), -od, -sd, -(rx + ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w // 2, h // 2)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_mv = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Maximize advantage vs opponent; avoid stepping onto opponent.
        opp_hit = 1 if (nx, ny) == (ox, oy) else 0
        val = (od - sd) - (0.5 * opp_hit) - (0.05 * cheb(nx, ny, ox, oy)) - (0.001 * (abs(dx) + abs(dy)))
        if best_val is None or val > best_val or (val == best_val and (dx, dy) > best_mv):
            best_val = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]