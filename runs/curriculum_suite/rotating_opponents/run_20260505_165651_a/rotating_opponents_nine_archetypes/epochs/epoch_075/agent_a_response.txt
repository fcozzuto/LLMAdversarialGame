def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs or not inb(x, y)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def clamp_step(dx):
        return 0 if dx == 0 else (1 if dx > 0 else -1)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        dx = clamp_step(ox - sx)
        dy = clamp_step(oy - sy)
        return [-dx, -dy]

    valid_resources = [(r[0], r[1]) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2 and inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not valid_resources:
        return [0, 0]

    # Score heuristic: prefer resources where we are closer than opponent, and avoid moving into "opponent sweep" alignment.
    # Also account for obstacle proximity.
    def cell_obstacle_pressure(x, y):
        # small penalty for near obstacles to avoid awkward detours
        p = 0
        for ex in (x-1, x, x+1):
            for ey in (y-1, y, y+1):
                if (ex, ey) in obs:
                    p += 1
        return p

    def best_target_value(px, py):
        best = None
        for tx, ty in valid_resources:
            sd = man(px, py, tx, ty)
            od = man(ox, oy, tx, ty)
            # "race" preference
            lead = od - sd  # bigger is better
            # encourage diagonal-ish routes a bit to break row-sweeps
            diag = abs((tx - px) - (ty - py))
            # small penalty if target is behind opponent in a row/col sense (likely sweep advantage)
            aligned = (ty == oy) or (tx == ox)
            value = (lead, -sd, -diag, -cell_obstacle_pressure(tx, ty), -int(aligned))
            if best is None or value > best[0]:
                best = (value, (tx, ty))
        return best[0]

    best_move = (0, 0)
    best_score = (-10**18, -10**18, -10**18, -10**18, -10**18)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # Anti-sweep: if we move to share row with opponent, avoid unless it improves the race strongly.
        row_align = int(ny == oy)
        col_align = int(nx == ox)
        # Encourage progress: evaluate from next position.
        tval = best_target_value(nx, ny)
        # Combine deterministically; prefer lower immediate proximity to opponent if race is equal.
        opp_close = -man(nx, ny, ox, oy)
        step_center = -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2)
        combined = (tval[0] - 2 * (row_align + col_align), tval[1], tval[2], opp_close - cell_obstacle_pressure(nx, ny), step_center)
        if combined > best_score:
            best_score = combined
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]