def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    pursuer = ("purs" in self_role) or ("tag" in self_role) or ("hunter" in self_role)
    if not pursuer:
        pursuer = ("purs" in opp_role) or ("tag" in opp_role) or ("hunter" in opp_role)

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    # likely evasion target: corner farthest from us
    tx, ty = max(corners, key=lambda c: (c[0] - sx) * (c[0] - sx) + (c[1] - sy) * (c[1] - sy))

    best_move = [0, 0]
    best_score = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in blocked:
                continue
            d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            d_corner = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)

            if pursuer:
                # intercept: push toward likely corner while closing on opponent
                score = -2.0 * d_opp - 0.6 * d_corner
            else:
                # evade: maximize distance from pursuer and head toward a corner
                # choose corner that is farthest from opponent to avoid easy intercept
                cx, cy = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
                d_corner2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
                score = 2.2 * d_opp + 0.5 * d_corner2

            if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = score
                best_move = [dx, dy]

    return best_move