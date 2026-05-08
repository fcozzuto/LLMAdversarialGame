def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    roles = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    is_pursuer = ("pursuer" in roles) or ("evader" not in roles)

    obs_list = observation.get("obstacles") or []
    obs = set()
    for p in obs_list:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist_metric(x, y, tx, ty):
        # Chebyshev tends to match diagonal reach in one step
        dx = abs(tx - x)
        dy = abs(ty - y)
        return dx if dx > dy else dy

    # Prefer escaping to the corner farthest from opponent (deterministic)
    far_corner = max(corners, key=lambda c: dist_metric(c[0], c[1], ox, oy))

    best = None
    best_val = None
    # Deterministic candidate ordering: dx,dy in fixed sequence
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not clamp_in(nx, ny):
                nx, ny = sx, sy
            d = dist_metric(nx, ny, ox, oy)
            if is_pursuer:
                # Minimize distance; tie-break toward opponent direction; then toward own corner (stable)
                dir_bonus = (abs((ox - nx)) - abs((ox - sx))) + (abs((oy - ny)) - abs((oy - sy)))
                corner_push = dist_metric(nx, ny, 0, 0) + dist_metric(nx, ny, w - 1, h - 1)
                val = (-d, -dir_bonus, corner_push)
                if best_val is None or val > best_val:
                    best_val = val
                    best = [dx, dy]
            else:
                # Maximize distance; tie-break toward far_corner; then away from opponent on both axes
                corner_dist = dist_metric(nx, ny, far_corner[0], far_corner[1])
                away = (abs(nx - ox) + abs(ny - oy)) - (abs(sx - ox) + abs(sy - oy))
                val = (d, corner_dist, away)
                if best_val is None or val > best_val:
                    best_val = val
                    best = [dx, dy]
    return [int(best[0]), int(best[1])]