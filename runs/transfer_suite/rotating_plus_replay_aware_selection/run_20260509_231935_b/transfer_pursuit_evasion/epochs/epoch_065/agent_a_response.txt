def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("evader" not in self_role and "pursuer" not in opp_role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if i_am_pursuer:
        # Pursue while avoiding obstacles; prefer moves that reduce distance most.
        best = None
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            # Small tie-break to avoid staying put and reduce boundary hits deterministically.
            tie = (0 if (dx, dy) != (0, 0) else 1)
            # Encourage moving along a line toward opponent (deterministic).
            step_align = -abs((ox - nx) - (oy - ny))
            val = (d, tie, -step_align)
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)
        return list(best if best is not None else (0, 0))
    else:
        # Evade: maximize distance from pursuer while avoiding obstacles; also bias away from center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            edge = abs(nx - cx) + abs(ny - cy)  # deterministic corner-ish bias
            stay_pen = 1 if (dx, dy) == (0, 0) else 0
            # Prefer larger distance, then larger edge bias, then non-staying, then deterministic order.
            val = (-d, -edge, stay_pen)
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)
        return list(best if best is not None else (0, 0))