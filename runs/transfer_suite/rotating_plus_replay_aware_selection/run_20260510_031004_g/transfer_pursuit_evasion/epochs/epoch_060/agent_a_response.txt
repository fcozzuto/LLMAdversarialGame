def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = True
    if "evad" in self_role:
        is_pursuer = False
    elif "evad" in opponent_role:
        is_pursuer = True

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner_from_opp = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    target_corner_for_evader = far_corner_from_opp
    target_corner_for_pursuer = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = (0, 0)
    best_score = -10**18 if is_pursuer else -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy

        px, py = target_corner_for_pursuer if is_pursuer else target_corner_for_evader
        corner_d = (nx - px) * (nx - px) + (ny - py) * (ny - py)

        center_d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        if is_pursuer:
            score = (-dist2) + 0.02 * (-corner_d) + 0.005 * (-center_d)
        else:
            score = (dist2) + 0.02 * (-corner_d) + 0.005 * (-center_d)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]