def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    sr = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in sr) or ("hunter" in sr) or ("pred" in sr)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def obst_risk(x, y):
        r = 0
        for ex, ey in obs:
            dx, dy = x - ex, y - ey
            d2 = dx * dx + dy * dy
            if d2 == 0:
                return 10**9
            if d2 <= 9:  # within 3
                r += (10 - d2)
        return r

    # Choose a target corner deterministically to change strategy from pure chasing.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    idx = (int(observation.get("turn_index", 0) or 0) // 3) % 4
    corners_order = corners[idx:] + corners[:idx]
    # For pursuer: aim near opponent (primary). For evader: aim for farthest corner (primary).
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d2_to_op = dist2(nx, ny, ox, oy)
        risk = obst_risk(nx, ny)

        if is_pursuer:
            # Chase while avoiding obstacles; slight tie-break toward reducing both axes.
            val = -d2_to_op - 0.08 * risk - 0.001 * (abs(nx - ox) + abs(ny - oy))
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        else:
            # Flee to a corner far from pursuer, with obstacle avoidance.
            tcx, tcy = corners_order[0]
            # pick best corner among order deterministically by farthest distance from opponent
            best_corner = None
            best_corner_d2 = None
            for cx, cy in corners_order:
                cd2 = dist2(cx, cy, ox, oy)
                if best_corner_d2 is None or cd2 > best_corner_d2:
                    best_corner_d2 = cd2
                    best_corner = (cx, cy)
            cx, cy = best_corner
            # Encourage moving away from opponent and toward escape corner.
            val = 1.2 * d2_to_op - 0.12 * risk - 0.0015 * dist2(nx, ny, cx, cy)
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]