def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    def is_pursuer(role):
        r = role.replace("-", "_")
        return ("purs" in r) or (r == "pursuer")
    def is_evader(role):
        r = role.replace("-", "_")
        return ("evad" in r) or (r == "evader")

    pursuer = is_pursuer(self_role) and not is_evader(self_role)
    if not pursuer and is_pursuer(opp_role) and not is_evader(opp_role):
        pursuer = False
    elif not pursuer and is_pursuer(opp_role) and is_evader(opp_role):
        pursuer = True
    elif pursuer and is_evader(self_role):
        pursuer = False

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
    near_corner = min(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = far_corner
    nx, ny = near_corner

    best = None
    best_score = None
    candidates = []
    for dx, dy in deltas:
        tx, ty = sx + dx, sy + dy
        if in_bounds(tx, ty) and (tx, ty) not in obs:
            candidates.append((dx, dy, tx, ty))
    if not candidates:
        for dx, dy in deltas:
            tx, ty = sx + dx, sy + dy
            if in_bounds(tx, ty):
                candidates.append((dx, dy, tx, ty))

    if pursuer:
        for dx, dy, tx, ty in candidates:
            d = dist2(tx, ty, ox, oy)
            tie = dist2(tx, ty, nx, ny)
            # Prefer minimizing distance; break ties by steering away from opponent's likely corner.
            score = (d, tie, abs(tx - ox) + abs(ty - oy))
            if best_score is None or score < best_score:
                best_score = score
                best = [dx, dy]
    else:
        for dx, dy, tx, ty in candidates:
            d = dist2(tx, ty, ox, oy)
            to_corner = dist2(tx, ty, cx, cy)
            # Prefer maximizing distance; break ties by moving toward the farthest corner.
            score = (-d, to_corner, abs(tx - cx) + abs(ty - cy))
            if best_score is None or score < best_score:
                best_score = score
                best = [dx, dy]

    return [int(best[0]), int(best[1])]