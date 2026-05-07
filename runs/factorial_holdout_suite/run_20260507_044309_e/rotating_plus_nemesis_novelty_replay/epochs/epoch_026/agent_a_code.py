def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not res:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach no later than opponent; then closer to us.
        key = (sd - od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            cur = cheb(nx, ny, tx, ty)
            # Secondary objective: reduce opponent's opportunity by moving toward a resource they likely contest
            opp_to_target = cheb(ox, oy, tx, ty)
            candidates.append(((cur - opp_to_target), cur, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]