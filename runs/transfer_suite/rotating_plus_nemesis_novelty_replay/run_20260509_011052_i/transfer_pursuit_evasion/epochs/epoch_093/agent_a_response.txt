def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    role = (observation.get("self_role") or "").lower()
    pursuing = (role != "evader")

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obs
    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Corner preference to limit escape routes when pursuing; opposite when evading.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if pursuing:
        cx, cy = min(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))
        target = (cx, cy)
    else:
        cx, cy = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))
        target = (sx, sy)  # keep safe; will bias away from opponent below

    best = None
    best_score = None

    # Intercept bias: aim for a cell that reduces both distance and approach angle.
    # Since we lack opponent velocity, use a deterministic "ahead" toward nearest corner.
    if pursuing:
        stepx = 0 if ox == cx else (1 if ox < cx else -1)
        stepy = 0 if oy == cy else (1 if oy < cy else -1)
        ahead = (ox + stepx, oy + stepy)
        ax, ay = ahead if inb(ahead[0], ahead[1]) else (ox, oy)
    else:
        ax, ay = ox, oy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_opp2 = dist2(nx, ny, ox, oy)

        # Move quality: pursue minimizes distance; evader maximizes it.
        # Obstacle-aware bias: slight penalty for getting too close to obstacles (deterministic).
        near_obs = 0
        for oxp, oyp in obstacles:
            if abs(nx - oxp) <= 1 and abs(ny - oyp) <= 1 and (nx, ny) != (oxp, oyp):
                near_obs += 1

        # Angle/corner bias
        corner_bias = dist2(nx, ny, target[0], target[1])
        if pursuing:
            ahead_bias = dist2(nx, ny, ax, ay)
            score = (d_opp * 1000 + d_opp2) + ahead_bias * 0.1 + corner_bias * 0.001 + near_obs * 5
            better = (best is None) or (score < best_score)
        else:
            # Evade: maximize distance to opponent and increase separation from their "ahead" direction
            sep = d_opp * 1000 + d_opp2
            away_bias = -dist2(nx, ny, ax, ay)
            score = (-sep) + away_bias * 0.1 + corner_bias * 0.0001 - near_obs * 5
            # For evader, higher sep is better => lower score (since we negate sep)
            better = (best is None) or (score < best_score)

        if better:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]