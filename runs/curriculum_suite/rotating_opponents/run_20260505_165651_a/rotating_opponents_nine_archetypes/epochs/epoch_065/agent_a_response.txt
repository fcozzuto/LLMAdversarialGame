def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            obj = md(nx, ny, cx, cy) + 0.01 * md(nx, ny, ox, oy)
            if best is None or obj < best or (obj == best and (dx, dy) < tuple(best_move)):
                best, best_move = obj, [dx, dy]
        return best_move

    best = None
    best_move = [0, 0]
    opp_corner = (0, 0) if (ox + oy) > (w - 1 - ox + h - 1 - oy) else (w - 1, h - 1)
    # Prefer moves that reduce my distance to the "best" resource for me, while increasing opp distance.
    # Tie-break deterministically by move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # If staying put keeps getting blocked positions near us, discourage landing adjacent to obstacles too much.
        obs_adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    obs_adj += 1
        my_opp = []
        # Evaluate the best resource for us at this next position
        best_obj_for_pos = None
        for rx, ry in resources:
            d1 = md(nx, ny, rx, ry)
            d2 = md(ox, oy, rx, ry)
            # If we can reach much sooner than opponent, prioritize strongly.
            # Also bias to avoid overly far moves when score is tight.
            obj = d1 - 1.35 * d2
            if best_obj_for_pos is None or obj < best_obj_for_pos:
                best_obj_for_pos = obj
        # Mildly encourage moving away from opponent's likely corner to break pursuit lines.
        away = md(nx, ny, opp_corner[0], opp_corner[1])
        obj_total = best_obj_for_pos - 0.02 * away + 0.06 * obs_adj
        if best is None or obj_total < best or (obj_total == best and (dx, dy) < tuple(best_move)):
            best, best_move = obj_total, [dx, dy]

    return best_move