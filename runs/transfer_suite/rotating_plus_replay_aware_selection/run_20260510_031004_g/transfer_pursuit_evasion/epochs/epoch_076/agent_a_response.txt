def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or (("evad" not in self_role) and ("evad" in opp_role) is False)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_pen(nx, ny):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x, y = nx + ax, ny + ay
                if 0 <= x < w and 0 <= y < h and (x, y) in obstacles:
                    pen += 1
        return pen

    best_score = None
    best_move = [0, 0]
    # Deterministic tie-breaker order already in moves; add small directional bias to avoid oscillation
    bias_x = 1 if (ox > sx) else (-1 if (ox < sx) else 0)
    bias_y = 1 if (oy > sy) else (-1 if (oy < sy) else 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, far_corner[0], far_corner[1])
        pen = obstacle_pen(nx, ny)

        if is_pursuer:
            # Chase with slight preference to reduce corner-distance (helps cut off)
            score = (-d_opp) + (-0.1 * d_corner) - (2.0 * pen)
        else:
            # Evade: maximize distance, also drift toward far corner; avoid walls/obstacles
            score = (d_opp) + (-0.07 * d_corner) - (2.0 * pen)

        score += 0.001 * (dx * bias_x + dy * bias_y)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move