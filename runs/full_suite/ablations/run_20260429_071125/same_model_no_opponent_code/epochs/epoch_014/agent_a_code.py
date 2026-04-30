def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obs = {(p[0], p[1]) for p in obstacles}
    res = [(p[0], p[1]) for p in resources]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if res:
        # Choose a resource where we are (or least behind) deterministically by advantage.
        best_r = res[0]
        best_key = None
        for rx, ry in res:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = od - sd  # positive means we are closer
            # Key prefers: more lead, then closer absolute, then deterministic tie by coords
            key = (lead, -abs(sd), -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        # No visible resources: head toward center while keeping distance from opponent a bit.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_mv = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        d_opp_after = cheb(nx, ny, ox, oy)
        collected = 1 if (nx, ny) in {(rx, ry) for (rx, ry) in res} else 0

        # If contested, prefer moves that reduce opponent access to target (increase opp distance to us).
        # Main objective: reduce our distance to target; secondary: discourage opponent proximity.
        val = (
            1000 * collected
            + (50 - d_self)
            + (10 if d_self <= cheb(x, y, tx, ty) else 0)
            + (0.5 * cheb(nx, ny, tx, ty) * 0)  # keep deterministic placeholder effect-free
            + (2.0 * (d_opp_after - cheb(x, y, ox, oy)))
            - 0.1 * cheb(nx, ny, tx, ty)
            + (5.0 * (d_opp - cheb(ox, oy, tx, ty)))
        )

        # Deterministic tie-break: prefer smaller dx, then smaller dy toward consistency.
        tie = best_val is not None and abs(val - best_val) < 1e-9
        if best_val is None or val > best_val or (tie and (dx, dy) < best_mv):
            best_val = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]