def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_target():
        if not resources:
            return None
        best = None
        best_val = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Prefer resources where we are closer and keep some control if opponent is also close.
            val = (opd - myd) * 2 - myd * 0.15 - opd * 0.05
            # Small tie-break toward center to reduce getting cornered near walls/obstacles.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val -= 0.02 * (abs(rx - cx) + abs(ry - cy))
            if val > best_val:
                best_val = val
                best = (rx, ry)
        return best

    target = best_target()
    if target is None:
        # No resources: move to reduce distance to opponent (deterministic contest).
        tx, ty = ox, oy
    else:
        tx, ty = target

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            # Engine keeps in place; treat as invalid by heavy penalty.
            score = -10**8
        else:
            my_to_t = md(nx, ny, tx, ty)
            opp_to_t = md(ox, oy, tx, ty)
            # Greedy toward target, but if opponent is currently closer, bias to block/intercept.
            opp_to_self = md(ox, oy, nx, ny)
            # Prefer moves that also make us closer to the opponent when opponent threatens the target.
            threat = 1.0 if opp_to_t < (md(sx, sy, tx, ty) + 1) else 0.0
            score = -my_to_t * 1.2 + (opp_to_t - my_to_t) * 0.35 + (opp_to_self * -0.05) + threat * (opp_to_self * 0.12) * (-1)
            # Mild obstacle-aware preference: avoid positions adjacent to obstacles.
            adj = 0
            for ax, ay in dirs:
                xx, yy = nx + ax, ny + ay
                if inb(xx, yy) and (xx, yy) in obstacles:
                    adj += 1
            score -= adj * 0.08
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]