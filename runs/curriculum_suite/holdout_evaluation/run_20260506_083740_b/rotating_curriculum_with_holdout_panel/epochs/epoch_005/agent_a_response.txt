def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Pick a target resource where we are more likely to secure it; if none, pick a deny/contest target.
    best_target = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd
        score = (margin, -sd, -od)
        if best_target is None or score > best_target[0]:
            best_target = (score, rx, ry)

    # If all targets are effectively worse (we're never ahead), switch to deny: minimize opponent access.
    target_margin = best_target[0][0]
    deny_mode = target_margin <= 0

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate by best resource we can reach relative to opponent, from the candidate position.
        if deny_mode:
            # Minimize opponent distance to the resources we move toward, while keeping some progress for ourselves.
            local = None
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Prefer resources where opponent is "closer" (deny) but we also progress.
                val = (-od, sd, -(od - sd))
                if local is None or val > local[0]:
                    local = (val, rx, ry)
            val = local[0]
        else:
            # Attack: maximize (opp_dist - self_dist) on the best target; tie-break for self closeness.
            local = None
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                margin = od - sd
                val = (margin, -sd, -od)
                if local is None or val > local[0]:
                    local = (val, rx, ry)
            val = local[0]

        # Stability tie-break: prefer moves that don't move "into a pocket" near obstacles.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    adj += 1
        val = (val[0], val[1], val[2], -adj, -cheb(nx, ny, ox, oy))

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move