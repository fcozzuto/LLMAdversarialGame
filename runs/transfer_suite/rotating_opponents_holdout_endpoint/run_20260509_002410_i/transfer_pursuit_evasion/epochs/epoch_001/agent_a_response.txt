def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [7, 7])
    x, y = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])
    obstacles = observation.get("obstacles", [])
    obs = set((int(a), int(b)) for a, b in obstacles)

    deltas = [[0, 0],[1, 0],[-1, 0],[0, 1],[0, -1],[1, 1],[-1, -1],[1, -1],[-1, 1]]
    my_role = observation.get("self_role", "")
    is_pursuer = ("pursuer" in str(my_role).lower()) or ("pursue" in str(my_role).lower())

    def dist(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    candidates = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    best = None
    best_score = None
    if is_pursuer:
        for dx, dy, nx, ny in candidates:
            d = dist(nx, ny, ox, oy)
            # prefer moves that reduce distance; slight preference to keeping center-ish
            center_bias = (3.5 - nx) * (3.5 - nx) + (3.5 - ny) * (3.5 - ny)
            score = (d, center_bias, dx, dy)
            if best is None or score < best_score:
                best, best_score = (dx, dy), score
    else:
        # evader: maximize distance from pursuer, avoid getting stuck near obstacles by mild border penalty
        for dx, dy, nx, ny in candidates:
            d = dist(nx, ny, ox, oy)
            border = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            score = (-d, border, dx, dy)
            if best is None or score < best_score:
                best, best_score = (dx, dy), score

    return [int(best[0]), int(best[1])]