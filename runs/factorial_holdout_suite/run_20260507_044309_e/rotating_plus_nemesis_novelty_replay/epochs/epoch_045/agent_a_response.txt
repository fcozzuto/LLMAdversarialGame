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
        dy = ay - by
        return (dx if dx >= 0 else -dx) if (dx if dx >= 0 else -dx) > (dy if dy >= 0 else -dy) else (dy if dy >= 0 else -dy)

    def best_target():
        best = None
        best_key = None
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            key = (adv, -ds, -rx, -ry)  # deterministic
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_target()
    if tx is None:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = [0, 0]
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ds_next = cheb(nx, ny, tx, ty)
        do_curr = cheb(ox, oy, tx, ty)
        adv = do_curr - ds_next
        dist_to_opp = cheb(nx, ny, ox, oy)
        key = (adv, -ds_next, dist_to_opp, -dx, -dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = [dx, dy]

    return [int(best_m[0]), int(best_m[1])]