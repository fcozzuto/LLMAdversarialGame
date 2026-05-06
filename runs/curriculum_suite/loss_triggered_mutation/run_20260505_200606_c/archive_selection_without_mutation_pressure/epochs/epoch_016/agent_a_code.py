def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best_move = (0, 0)
    best_val = None

    # Opponent's likely next target (nearest resource)
    opp_target = min(resources, key=lambda r: man(ox, oy, r[0], r[1]))
    tx, ty = opp_target

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Score by contesting resources: maximize (opp_dist - our_dist)
        # plus a bias toward the opponent's nearest target to intercept.
        our_to_target = man(nx, ny, tx, ty)
        our_best_d = 10**9
        margin_best = -10**9
        for rx, ry in resources:
            od = man(ox, oy, rx, ry)
            dd = man(nx, ny, rx, ry)
            if dd < our_best_d:
                our_best_d = dd
            m = od - dd
            if m > margin_best:
                margin_best = m

        # If we can't contest well, fall back to nearest resource, still preferring target.
        val = margin_best * 1000 - our_best_d * 5 - our_to_target
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: prefer moves that reduce distance to opponent's target, then lexicographically.
            ct = man(nx, ny, tx, ty)
            bt = man(sx + best_move[0], sy + best_move[1], tx, ty)
            if ct < bt or (ct == bt and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]