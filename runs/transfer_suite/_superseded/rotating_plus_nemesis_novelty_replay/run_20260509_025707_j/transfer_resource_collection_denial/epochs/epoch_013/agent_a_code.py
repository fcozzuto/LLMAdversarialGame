def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Pick a target the opponent is not strictly faster to reach (race advantage first).
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (od - sd, -sd, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Score each move by its improvement in race for the best reachable resource.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate against all visible resources (still cheap: <=12).
        best_local = None
        for tr, ty in resources:
            sd = man(nx, ny, tr, ty)
            od = man(ox, oy, tr, ty)
            # Encourage closing on something while keeping/expanding opponent disadvantage.
            val = (od - sd, -sd, -(tr + ty))
            if best_local is None or val > best_local:
                best_local = val
        # Additional tie-break: prefer moves toward chosen target to reduce path drift.
        sd_t = man(nx, ny, rx, ry)
        self_d_t = man(sx, sy, rx, ry)
        drift_bonus = (self_d_t - sd_t)
        final = (best_local[0], best_local[1], drift_bonus, -abs(nx - rx) - abs(ny - ry))
        if best_val is None or final > best_val:
            best_val = final
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]