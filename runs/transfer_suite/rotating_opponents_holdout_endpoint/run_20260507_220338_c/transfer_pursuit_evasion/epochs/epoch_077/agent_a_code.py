def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_evader = not any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    # Heuristic: if pursuing, go toward opponent; if evading, go away and bias to center/corner escape.
    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = (0, 0)
    best_val = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Distance to opponent (Chebyshev for grid evasion/pursuit feel)
        ddx = abs(nx - ox)
        ddy = abs(ny - oy)
        dist = ddx if ddx >= ddy else ddy

        # Secondary: keep away from walls and prefer center when evading
        wall_pen = 0.0
        if nx in (0, w - 1):
            wall_pen += 0.35
        if ny in (0, h - 1):
            wall_pen += 0.35
        center_pen = ((nx - cx) ** 2 + (ny - cy) ** 2) ** 0.5

        # If pursuing: minimize dist; if evading: maximize dist.
        # Add tie-breakers deterministically.
        if i_am_evader:
            val = dist
            val += 0.08 * center_pen  # move toward center (safe vs corner evasion)
            val += 0.05 * wall_pen    # slightly prefer less wall contact
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < best)
        else:
            val = -dist
            val -= 0.08 * center_pen  # less relevant, but biases straight pursuit
            val -= 0.05 * wall_pen
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < best)

        if better:
            best_val = val
            best = (dx, dy)

    # If all candidate moves were invalid, stay.
    return [int(best[0]), int(best[1])]