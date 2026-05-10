def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    evade = ("evad" in self_role) or (self_role == "evader") or (("evad" in opponent_role) or (opponent_role == "evader" and not ("purs" in self_role)))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best_score = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        corner_dist = max(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
        # Small obstacle-avoidance: count open neighbors
        open_n = 0
        for adx, ady in deltas:
            tx, ty = nx + adx, ny + ady
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obs:
                open_n += 1
        if evade:
            score = (d, corner_dist, open_n, -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2))
        else:
            score = (-d, corner_dist * 0.001, open_n, -abs(nx - ox) - abs(ny - oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]